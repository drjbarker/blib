# -*- coding: utf-8 -*-
from tex.encoding import encode_tex_specials, encode_tex_diacritics

from unittest import TestCase


class TestEncodeTexSpecials(TestCase):
    def test_encode_tex_specials(self):
        cases = {
            "α": r"$\alpha$",  # U+03B1 greek small letter alpha
            "σ": r"$\sigma$",  # U+03C3 greek small letter sigma

            "å": r"{\aa}", # U+00E5 latin small letter a with ring above
            "ı": r"{\i}",  # U+0131 latin small letter dotless i
            "Ł": r"{\L}",  # U+0142 latin capital letter l with stroke
            "ł": r"{\l}",  # U+0142 latin small letter l with stroke
            "¡": r"{!`}",  # U+00A1 inverted exclamation mark
            "¿": r"{?`}",  # U+00BF inverted question mark
            "Ø": r"{\O}",  # U+00F8 latin capital letter o with stroke
            "ø": r"{\o}",  # U+00F8 latin small letter o with stroke
            "ß": r"{\ss}", # U+00DF latin small letter sharp s

            " ": r" ",  # U+2009 thin space
            "‐": r"-",     # U+2010 hyphen
            "‑": r"-",     # U+2011 non-breaking hyphen
            "‒": r"-",     # U+2012 figure dash
            "–": r"--",    # U+2013 en dash
            "—": r"---",   # U+2013 em dash
            "‘": r"`",     # U+2018 left single quotation mark
            "’": r"'",     # U+2019 right single quotation mark
            "“": r"``",    # U+201C left double quotation mark
            "”": r"''",    # U+201D right double quotation mark

            "ﬁ": r"fi",    # U+FB01 latin small ligature fi
            "ﬂ": r"fl",    # U+FB02 latin small ligature fl
            "ﬃ": r"ffi",  # U+FB03 latin small ligature ffi
            "ﬄ": r"ffl",  # U+FB04 latin small ligature ffl
        }

        for unicode, tex in cases.items():
            self.assertEqual(encode_tex_specials(unicode), tex)

    def test_encode_tex_diacritics(self):
        cases = {
            'å': r'{\r a}',
            'é': r'{\'e}',
            'è': r'{\`e}',
            'ê': r'{\^e}',
            'ë': r'{\"e}',
            'ē': r'{\=e}',
            'ė': r'{\.e}',
            'ę': r'{\k e}',
            'ç': r'{\c c}',
            'č': r'{\v c}',
            'ñ': r'{\~n}'
        }

        for unicode, tex in cases.items():
            self.assertEqual(encode_tex_diacritics(unicode), tex)

