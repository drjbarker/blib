import json
from dataclasses import dataclass
from typing import Optional
from urllib.error import URLError
from urllib.request import Request, urlopen

from blib.resourceid import ResourceId, ResourceIdType
from blib.providers.provider import Provider

BLIB_HTTP_USER_AGENT = r'blib/0.1 (https://github.com/drjbarker/blib; mailto:j.barker@leeds.ac.uk)'


@dataclass
class OrcidWork:
    doi: str
    year: Optional[int]
    month: Optional[int]
    day: Optional[int]
    position: int


class OrcidProvider(Provider):
    def request(self, orcid):
        url = f'https://pub.orcid.org/v3.0/{orcid}/works'
        with urlopen(Request(url, headers={
            'User-Agent': BLIB_HTTP_USER_AGENT,
            'Accept': 'application/json',
        })) as response:
            if response.code != 200:
                raise URLError(f"failed to resolve {url}")

            data = json.loads(response.read().decode('utf-8'))

        works = self._parse_works(data)
        return [ResourceId(work.doi, ResourceIdType.doi) for work in works]

    def _parse_works(self, data):
        unique_works = {}

        for position, group in enumerate(data.get('group', [])):
            work = self._work_from_group(group, position)
            if work is None:
                continue

            if work.doi not in unique_works:
                unique_works[work.doi] = work
                continue

            existing = unique_works[work.doi]
            if self._sort_key(work) < self._sort_key(existing):
                unique_works[work.doi] = work

        return sorted(unique_works.values(), key=self._sort_key)

    def _work_from_group(self, group, position):
        summary = self._preferred_summary(group)
        if summary is not None:
            doi = self._first_doi(summary.get('external-ids', {}))
            if doi:
                year, month, day = self._summary_publication_date(summary)
                if year is None:
                    year, month, day = self._group_publication_date(group)
                return OrcidWork(
                    doi=doi.lower(),
                    year=year,
                    month=month,
                    day=day,
                    position=position,
                )

        doi = self._first_doi(group.get('external-ids', {}))
        if doi is None:
            return None

        year, month, day = self._group_publication_date(group)
        return OrcidWork(
            doi=doi.lower(),
            year=year,
            month=month,
            day=day,
            position=position,
        )

    def _sort_key(self, work):
        has_date = work.year is not None
        return (
            0 if has_date else 1,
            work.year if work.year is not None else 9999,
            work.month if work.month is not None else 99,
            work.day if work.day is not None else 99,
            work.position,
            work.doi,
        )

    def _group_publication_date(self, group):
        dates = []
        for summary in group.get('work-summary', []):
            year, month, day = self._summary_publication_date(summary)
            if year is None:
                continue

            completeness = sum(value is not None for value in (year, month, day))
            dates.append((year, month, day, -completeness))

        if not dates:
            return None, None, None

        year, month, day, _ = min(
            dates,
            key=lambda value: (
                value[0],
                value[1] if value[1] is not None else 99,
                value[2] if value[2] is not None else 99,
                value[3],
            )
        )
        return year, month, day

    def _summary_publication_date(self, summary):
        publication_date = summary.get('publication-date') or {}
        year = self._date_value(publication_date, 'year')
        month = self._date_value(publication_date, 'month')
        day = self._date_value(publication_date, 'day')
        return year, month, day

    def _date_value(self, publication_date, key):
        value = publication_date.get(key)
        if not value or value.get('value') is None:
            return None
        return int(value['value'])

    def _preferred_summary(self, group):
        summaries = group.get('work-summary', [])

        for summary in summaries:
            if self._is_crossref_summary(summary) and self._first_doi(summary.get('external-ids', {})):
                return summary

        for summary in summaries:
            if self._first_doi(summary.get('external-ids', {})):
                return summary

        return None

    def _is_crossref_summary(self, summary):
        source = summary.get('source') or {}
        source_name = source.get('source-name') or {}
        return str(source_name.get('value', '')).strip().lower() == 'crossref'

    def _first_doi(self, external_ids):
        dois = self._external_ids_to_dois(external_ids)
        if dois:
            return dois[0]
        return None

    def _external_ids_to_dois(self, external_ids):
        result = []
        for external_id in external_ids.get('external-id', []):
            if external_id.get('external-id-type', '').lower() != 'doi':
                continue

            normalized = external_id.get('external-id-normalized', {}) or {}
            value = normalized.get('value') or external_id.get('external-id-value')
            if value:
                result.append(value)

        return result
