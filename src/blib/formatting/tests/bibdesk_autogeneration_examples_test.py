from unittest import TestCase

from blib.encoding.unicode_encoder import UnicodeEncoder
from blib.formatting.bibdesk_autogeneration import (
    BibDeskAutogenerationFormatter,
    BibDeskFormatError,
)


DOCUMENTATION_BIBLIOGRAPHY = {
    'bibtex_type': 'article',
    'author': [
        {'given': 'M.', 'family': 'McCracken'},
        {'given': 'A.', 'family': 'Maxwell'},
        {'given': 'J.', 'family': 'Howison'},
        {'given': 'M.', 'family': 'Routley'},
        {'given': 'S.', 'family': 'Spiegel'},
        {'given': 'S. S.', 'family': 'Porst'},
        {'given': 'C. M.', 'family': 'Hofman'},
    ],
    'title': 'BibDesk, a great application to manage your bibliographies',
    'journal': 'Source Forge',
    'journal_abbreviation': 'Source Forge',
    'volume': '1',
    'pages': ['96'],
    'year': '2004',
    'month': '11',
}


class TestBibDeskAutogenerationDocumentationExamples(TestCase):
    def _formatter(self, format_string):
        return BibDeskAutogenerationFormatter(format_string, UnicodeEncoder(), citekey_mode=True)

    def test_example_truncated_authors_and_date(self):
        citation = self._formatter('%a 03%y%m').format(DOCUMENTATION_BIBLIOGRAPHY)

        self.assertEqual(citation, 'McCMaxHowRouSpiPorHof0411')

    def test_example_author_initials_and_title(self):
        # The BibDesk examples page shows `%y` producing `2004`, but the syntax table on the
        # same page defines `%y` as the year without the century. We follow the table semantics.
        citation = self._formatter('%A[;][.][;etal]2:%y%t 20').format(DOCUMENTATION_BIBLIOGRAPHY)

        self.assertEqual(citation, 'McCracken.M.;Maxwell.A.;etal:04BibDesk-a-great-appl')

    def test_example_field_acronym_and_volume(self):
        citation = self._formatter('%a[;][;etal]24:%c{Journal}%f{Volume}').format(DOCUMENTATION_BIBLIOGRAPHY)

        self.assertEqual(citation, 'McCr;Maxw;etal:SF1')

    def test_unique_number_example_is_not_supported_yet(self):
        with self.assertRaisesRegex(BibDeskFormatError, r'specifier %n is not supported'):
            self._formatter('%a 1:%Y%n').format(DOCUMENTATION_BIBLIOGRAPHY)

    def test_unique_lowercase_example_is_not_supported_yet(self):
        with self.assertRaisesRegex(BibDeskFormatError, r'specifier %u is not supported'):
            self._formatter('%a 1:%Y%u[Doi][Title]2').format(DOCUMENTATION_BIBLIOGRAPHY)
