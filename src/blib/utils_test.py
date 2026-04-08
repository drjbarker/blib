from unittest import TestCase

from blib.utils import normalise_mojibake_utf8, normalise_spacing_accents


class UtilsTest(TestCase):
    def test_normalise_mojibake_utf8(self):
        self.assertEqual(normalise_mojibake_utf8("Oâ\x80\x99Regan"), "O’Regan")
        self.assertEqual(normalise_mojibake_utf8("MoirÃ©"), "Moiré")
        self.assertEqual(normalise_mojibake_utf8("No change"), "No change")

    def test_normalise_spacing_accents(self):
        self.assertEqual(normalise_spacing_accents("Moir´e"), "Moiré")
        self.assertEqual(normalise_spacing_accents("Jos´e"), "José")
        self.assertEqual(normalise_spacing_accents("Oâ\x80\x99Regan"), "O’Regan")
        self.assertEqual(normalise_spacing_accents("No change"), "No change")
