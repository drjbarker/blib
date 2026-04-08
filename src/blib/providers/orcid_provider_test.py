from unittest import TestCase

from blib.providers.orcid_provider import OrcidProvider


class TestOrcidProvider(TestCase):
    def test_parse_works_deduplicates_and_sorts_chronologically(self):
        provider = OrcidProvider()

        payload = {
            'group': [
                {
                    'external-ids': {
                        'external-id': [
                            {
                                'external-id-type': 'doi',
                                'external-id-value': '10.1000/B',
                            }
                        ]
                    },
                    'work-summary': [
                        {
                            'publication-date': {
                                'year': {'value': '2025'},
                                'month': {'value': '03'},
                                'day': {'value': '10'},
                            }
                        }
                    ],
                },
                {
                    'work-summary': [
                        {
                            'external-ids': {
                                'external-id': [
                                    {
                                        'external-id-type': 'doi',
                                        'external-id-normalized': {'value': '10.1000/a'},
                                    }
                                ]
                            },
                            'publication-date': {
                                'year': {'value': '2024'},
                                'month': {'value': '12'},
                                'day': {'value': '01'},
                            }
                        }
                    ],
                },
                {
                    'external-ids': {
                        'external-id': [
                            {
                                'external-id-type': 'doi',
                                'external-id-normalized': {'value': '10.1000/b'},
                            }
                        ]
                    },
                    'work-summary': [
                        {
                            'publication-date': {
                                'year': {'value': '2025'},
                                'month': {'value': '02'},
                                'day': {'value': '20'},
                            }
                        }
                    ],
                },
                {
                    'external-ids': {
                        'external-id': [
                            {
                                'external-id-type': 'eid',
                                'external-id-value': '2-s2.0-123',
                            },
                            {
                                'external-id-type': 'doi',
                                'external-id-value': '10.1000/c',
                            }
                        ]
                    },
                    'work-summary': [
                        {
                            'publication-date': {
                                'year': None,
                                'month': None,
                                'day': None,
                            }
                        }
                    ],
                },
            ]
        }

        works = provider._parse_works(payload)

        self.assertEqual([work.doi for work in works], ['10.1000/a', '10.1000/b', '10.1000/c'])
        self.assertEqual((works[0].year, works[0].month, works[0].day), (2024, 12, 1))
        self.assertEqual((works[1].year, works[1].month, works[1].day), (2025, 2, 20))
        self.assertEqual((works[2].year, works[2].month, works[2].day), (None, None, None))

    def test_parse_works_prefers_crossref_source_and_returns_one_doi_per_group(self):
        provider = OrcidProvider()

        payload = {
            'group': [
                {
                    'work-summary': [
                        {
                            'source': {
                                'source-name': {'value': 'Scopus - Elsevier'},
                            },
                            'external-ids': {
                                'external-id': [
                                    {
                                        'external-id-type': 'doi',
                                        'external-id-value': '10.1000/elsevier',
                                    }
                                ]
                            },
                            'publication-date': {
                                'year': {'value': '2025'},
                                'month': {'value': '02'},
                                'day': {'value': '02'},
                            },
                        },
                        {
                            'source': {
                                'source-name': {'value': 'Crossref'},
                            },
                            'external-ids': {
                                'external-id': [
                                    {
                                        'external-id-type': 'doi',
                                        'external-id-value': '10.1000/crossref',
                                    }
                                ]
                            },
                            'publication-date': {
                                'year': {'value': '2025'},
                                'month': {'value': '01'},
                                'day': {'value': '15'},
                            },
                        },
                    ],
                },
                {
                    'work-summary': [
                        {
                            'source': {
                                'source-name': {'value': 'Joseph Barker via Scopus - Elsevier'},
                            },
                            'external-ids': {
                                'external-id': [
                                    {
                                        'external-id-type': 'doi',
                                        'external-id-value': '10.1000/first-source',
                                    },
                                    {
                                        'external-id-type': 'doi',
                                        'external-id-value': '10.1000/second-doi',
                                    }
                                ]
                            },
                            'publication-date': {
                                'year': {'value': '2024'},
                                'month': {'value': '10'},
                                'day': {'value': '05'},
                            },
                        },
                        {
                            'source': {
                                'source-name': {'value': 'Another Source'},
                            },
                            'external-ids': {
                                'external-id': [
                                    {
                                        'external-id-type': 'doi',
                                        'external-id-value': '10.1000/later-source',
                                    }
                                ]
                            },
                            'publication-date': {
                                'year': {'value': '2024'},
                                'month': {'value': '11'},
                                'day': {'value': '01'},
                            },
                        },
                    ],
                },
            ]
        }

        works = provider._parse_works(payload)

        self.assertEqual([work.doi for work in works], ['10.1000/first-source', '10.1000/crossref'])
        self.assertEqual((works[0].year, works[0].month, works[0].day), (2024, 10, 5))
        self.assertEqual((works[1].year, works[1].month, works[1].day), (2025, 1, 15))
