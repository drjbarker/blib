from unittest import TestCase

from blib.utils import normalise_spacing_accents


class UtilsTest(TestCase):
    def test_normalise_spacing_accents(self):
        self.assertEqual(normalise_spacing_accents("Moir´e"), "Moiré")
        self.assertEqual(normalise_spacing_accents("Jos´e"), "José")
        self.assertEqual(normalise_spacing_accents("No change"), "No change")
