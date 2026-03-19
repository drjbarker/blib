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
