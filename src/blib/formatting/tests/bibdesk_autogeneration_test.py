from unittest import TestCase

from blib.formatting.bibdesk_autogeneration import BibDeskAutogenerationFormatter
from blib.formatting.markdown import MarkdownFormatter
from blib.formatting.richtext import RichTextFormatter
from blib.formatting.text_formatter import TextFormatter


ARTICLE_DATA = {
    'bibtex_type': 'article',
    'author': [
        {'given': 'Joseph', 'family': 'Barker'},
        {'given': 'Anna Marie', 'family': 'Maxwell'},
        {'given': 'Chris', 'family': 'Jones'},
    ],
    'title': 'A study of magnetic materials',
    'journal': 'Journal of Interesting Results',
    'journal_abbreviation': 'J. Int. Results',
    'doi': '10.1000/example',
    'url': 'https://dx.doi.org/10.1000/example',
    'volume': '42',
    'number': '7',
    'pages': ['100', '108'],
    'publisher': 'Example Press',
    'year': '2024',
    'month': '11',
}


MISC_DATA = {
    'bibtex_type': 'misc',
    'author': [
        {'given': 'Jane', 'family': 'Doe'},
    ],
    'title': 'Preprint title',
    'journal': 'arXiv.2401.12345 [cond-mat]',
    'url': 'https://arxiv.org/abs/2401.12345',
    'eprint': '2401.12345',
    'archiveprefix': 'arXiv',
    'primaryclass': 'cond-mat',
    'year': 2024,
    'month': 1,
}


class TestBibDeskAutogenerationFormatter(TestCase):
    def test_author_title_and_year_template(self):
        formatter = TextFormatter(format_string='%A[, ][ ]2, %t (%Y)')

        citation = formatter.format(ARTICLE_DATA)

        self.assertEqual(citation, 'Barker J., Maxwell A.M., A study of magnetic materials (2024)')

    def test_title_word_and_field_specifiers(self):
        formatter = BibDeskAutogenerationFormatter(
            '%T[3]2 | %c{Journal} | %f{Pages} | %f{Journal Abbreviation} | %f{BibTeX Type}',
            TextFormatter()._encoder
        )

        citation = formatter.format(ARTICLE_DATA)

        self.assertEqual(citation, 'A study of magnetic | JIR | 100--108 | J. Int. Results | article')

    def test_markdown_custom_format_replaces_default_template(self):
        formatter = MarkdownFormatter(format_string='[%f{Cite Key}](%f{Url})')

        citation = formatter.format(ARTICLE_DATA)

        self.assertEqual(citation, '[Barker_JIntResults_42_100_2024](https://dx.doi.org/10.1000/example)')

    def test_etal_suffix_follows_bibdesk_separator_rules(self):
        formatter = TextFormatter(format_string='%A[;][.][;etal]2')

        citation = formatter.format(ARTICLE_DATA)

        self.assertEqual(citation, 'Barker.J.;Maxwell.A.M.;etal')

    def test_richtext_custom_format_is_rtf_encoded(self):
        formatter = RichTextFormatter(format_string='%A[, ][ ]1, %t')

        citation = formatter.format({
            **ARTICLE_DATA,
            'author': [{'given': 'Amalio', 'family': 'Fernández-Pacheco'}],
        })

        self.assertTrue(citation.startswith(r'{\pard '))
        self.assertIn(r'Fern\u225', citation)

    def test_misc_cite_key_is_available(self):
        formatter = TextFormatter(format_string='%f{Cite Key}')

        citation = formatter.format(MISC_DATA)

        self.assertEqual(citation, 'Doe_2401_12345_2024')

    def test_default_text_formatter_is_unchanged_without_format_string(self):
        formatter = TextFormatter(use_title=True)

        citation = formatter.format(ARTICLE_DATA)

        self.assertEqual(
            citation,
            'J. Barker et al., A study of magnetic materials, J. Int. Results 42, 100 (2024)'
        )
