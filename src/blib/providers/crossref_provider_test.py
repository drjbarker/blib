from unittest import TestCase

import blib.providers


class TestCrossrefSource(TestCase):
    def test_request(self):
        source = blib.providers.CrossrefProvider()

        print(source.request('10.1002/adma.202302419'))

    def test_normalise_result_upgrades_legacy_cached_schema(self):
        source = blib.providers.CrossrefProvider()
        result = {
            "entry": "article",
            "authors": [{"given": "Ada", "family": "Lovelace"}],
            "title": "Notes on the Analytical Engine",
            "journal": "Journal of Engines",
            "journal-abbrev": "J. Engines",
            "doi": "10.1000/example",
            "url": "https://dx.doi.org/10.1000/example",
            "issue": "2",
            "volume": "7",
            "pages": ["10", "19"],
            "publisher": "Example Press",
            "published-date": {"year": 2024, "month": 5},
        }

        self.assertEqual(
            source._normalise_result(result),
            {
                "bibtex_type": "article",
                "author": [{"given": "Ada", "family": "Lovelace"}],
                "title": "Notes on the Analytical Engine",
                "journal": "Journal of Engines",
                "journal_abbreviation": "J. Engines",
                "doi": "10.1000/example",
                "url": "https://dx.doi.org/10.1000/example",
                "number": "2",
                "volume": "7",
                "pages": ["10", "19"],
                "publisher": "Example Press",
                "year": "2024",
                "month": "5",
            },
        )
