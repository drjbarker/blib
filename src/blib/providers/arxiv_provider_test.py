import xml.etree.ElementTree as ET
from unittest import TestCase

import blib.providers


class TestArxivSource(TestCase):
    def test_request(self):
        source = blib.providers.ArxivProvider()

        print(source.request('2310.03169'))

    def test_title_normalises_spacing_accents(self):
        source = blib.providers.ArxivProvider()
        root = ET.fromstring("""
        <feed xmlns="http://www.w3.org/2005/Atom">
            <entry>
                <title>Moir´e excitons</title>
            </entry>
        </feed>
        """)

        self.assertEqual(source._title(root), "Moiré excitons")

    def test_authors_normalise_spacing_accents(self):
        source = blib.providers.ArxivProvider()
        root = ET.fromstring("""
        <feed xmlns="http://www.w3.org/2005/Atom">
            <entry>
                <author><name>Jos´e Alvarez</name></author>
            </entry>
        </feed>
        """)

        self.assertEqual(
            source._authors(root),
            [{"given": "José", "family": "Alvarez"}],
        )

    def test_authors_repair_mojibake_apostrophes(self):
        source = blib.providers.ArxivProvider()
        root = ET.fromstring("""
        <feed xmlns="http://www.w3.org/2005/Atom">
            <entry>
                <author><name>D. D. OâRegan</name></author>
            </entry>
        </feed>
        """)

        self.assertEqual(
            source._authors(root),
            [{"given": "D. D.", "family": "O’Regan"}],
        )

    def test_normalise_result_repairs_cached_mojibake(self):
        source = blib.providers.ArxivProvider()
        result = {
            "bibtex_type": "misc",
            "author": [{"given": "D. D.", "family": "Oâ\x80\x99Regan"}],
            "title": "MoirÃ© spin textures",
            "journal": "arXiv.1912.02712v2 [cond-mat.mtrl-sci]",
            "url": "https://arxiv.org/abs/1912.02712v2",
            "eprint": "1912.02712",
            "archiveprefix": "arXiv",
            "primaryclass": "cond-mat.mtrl-sci",
            "year": 2019,
            "month": 12,
        }

        self.assertEqual(
            source._normalise_result(result),
            {
                **result,
                "author": [{"given": "D. D.", "family": "O’Regan"}],
                "title": "Moiré spin textures",
            },
        )

    def test_normalise_result_upgrades_legacy_cached_schema(self):
        source = blib.providers.ArxivProvider()
        result = {
            "entry": "misc",
            "authors": [{"given": "Ada", "family": "Lovelace"}],
            "title": "Notes on the Analytical Engine",
            "journal": "arXiv.2603.08777v1 [cs.LG]",
            "url": "https://arxiv.org/abs/2603.08777v1",
            "eprint": "2603.08777v1",
            "archiveprefix": "arXiv",
            "primaryclass": "cs.LG",
            "published-date": {"year": 2026, "month": 3},
        }

        self.assertEqual(
            source._normalise_result(result),
            {
                "bibtex_type": "misc",
                "author": [{"given": "Ada", "family": "Lovelace"}],
                "title": "Notes on the Analytical Engine",
                "journal": "arXiv.2603.08777v1 [cs.LG]",
                "url": "https://arxiv.org/abs/2603.08777v1",
                "eprint": "2603.08777v1",
                "archiveprefix": "arXiv",
                "primaryclass": "cs.LG",
                "year": 2026,
                "month": 3,
            },
        )
