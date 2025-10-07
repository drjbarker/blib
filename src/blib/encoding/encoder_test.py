import re
from unittest import TestCase

from blib.encoding import Encoder


class TestEncoder(TestCase):
    def test_chemical_formula_regex(self):

        cases = [
            ("NiO", ""), # We only match chemical formula with numbers in.
            ("Fe2", "Fe2")
            ]

        encoder = Encoder()

        for test_text, expected_result in cases:
            match = re.search(Encoder._token_regex_chemical, test_text)
            matched_text = match.group(0) if match else ""
            self.assertEqual(matched_text, expected_result)
