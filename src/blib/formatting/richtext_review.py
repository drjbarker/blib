import blib.encoding
from .text_formatter import TextFormatter


class RichTextReviewFormatter(TextFormatter):

    def __init__(self,
                 abbreviate_journals=False,
                 use_title=True,
                 max_authors=100,
                 etal="et al."):
        TextFormatter.__init__(self,
                               abbreviate_journals=abbreviate_journals,
                               use_title=use_title,
                               max_authors=max_authors,
                               etal=f"\i {etal}\i0" if etal else "")
        self._encoder = blib.encoding.RichTextEncoder()

    def format(self, data):

        if data['entry'] == 'article':
            citation = self._format_article(data)
        else:
            citation = self._format_misc(data)

        return rf'{{\pard {citation} \par}}'

    def header(self):
        return r'{\rtf1\ansi\deff0 '

    def footer(self):
        return r'}'

    def _format_article(self, data):
        result = []

        if self._use_title:
            result.append(f"{self._encoder.encode(data['title'])}, ")

        authors = self._authors(data['authors'])

        if authors:
            result.append(f"{self._authors(data['authors'])}, ")

        if self._abbreviate_journals:
            result.append(f"{self._encoder.encode(data['journal-abbrev'])}")
        else:
            result.append(f"{self._encoder.encode(data['journal'])}")

        result.append(f" \\b {data['volume']}\\b0")

        if data['pages']:
            try:
                result.append(f", {data['pages'][0]} ")
            except TypeError:
                result.append(f", {data['pages']} ")
        else:
            result.append(f"  ")

        result.append(f"({data['published-date']['year']}); ")

        result.append(f"https://doi.org/{data['doi']}")

        return ''.join(result)

    def _format_misc(self, data):
        result = []

        if self._use_title:
            result.append(f"{self._encoder.encode(data['title'])}, ")

        authors = self._authors(data['authors'])

        if authors:
            result.append(f"{self._authors(data['authors'])}, ")

        if self._abbreviate_journals:
            result.append(f"{self._encoder.encode(data['journal-abbrev'])}")
        else:
            result.append(f"{self._encoder.encode(data['journal'])}")

        if 'volume' in data:
            result.append(f" \\b {data['volume']}\\b0")

        if 'pages' in data:
            if data['pages']:
                try:
                    result.append(f", {data['pages'][0]} ")
                except TypeError:
                    result.append(f", {data['pages']} ")
            else:
                result.append(f"  ")

        result.append(f" ({data['published-date']['year']}); ")

        if 'doi' in data:
            result.append(f"https://doi.org/{data['doi']}")
        elif 'url' in data:
            result.append(f"{data['url']}")

        return ''.join(result)
