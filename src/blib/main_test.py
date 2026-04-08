import io
from urllib.error import URLError
from unittest import TestCase
from unittest.mock import MagicMock, patch

from blib.main import is_valid_orcid, main
from blib.resourceid import ResourceId, ResourceIdType


class TestMain(TestCase):
    def test_is_valid_orcid_accepts_expected_format(self):
        self.assertEqual(is_valid_orcid('0000-0003-4843-5516'), '0000-0003-4843-5516')

    def test_is_valid_orcid_rejects_invalid_format(self):
        with self.assertRaisesRegex(Exception, 'ORCID must be in the format'):
            is_valid_orcid('0000-0003-4843-XXXX')

    def test_orcid_mode_processes_dois_and_continues_after_failures(self):
        orcid_resolver = MagicMock()
        orcid_resolver.request.return_value = [
            ResourceId('10.1000/a', ResourceIdType.doi),
            ResourceId('10.1000/bad', ResourceIdType.doi),
            ResourceId('10.1000/b', ResourceIdType.doi),
        ]

        doi_resolver = MagicMock()
        doi_resolver.request.side_effect = [
            {'doi': '10.1000/a'},
            URLError('not found'),
            {'doi': '10.1000/b'},
        ]

        with patch('sys.argv', ['blib', '--output', 'doi', '--no-clip', '--orcid', '0000-0003-4843-5516']), \
             patch('blib.main.blib.providers.OrcidProvider', return_value=orcid_resolver), \
             patch('blib.main.blib.providers.CrossrefProvider', return_value=doi_resolver), \
             patch('blib.main.blib.providers.ArxivProvider'), \
             patch('sys.stdout', new_callable=io.StringIO) as stdout:
            main()

        output = stdout.getvalue()

        orcid_resolver.request.assert_called_once_with('0000-0003-4843-5516')
        self.assertIn('10.1000/a', output)
        self.assertIn('// failed DOI lookup: 10.1000/bad', output)
        self.assertIn('10.1000/b', output)
        self.assertLess(output.find('10.1000/a'), output.find('// failed DOI lookup: 10.1000/bad'))
        self.assertLess(output.find('// failed DOI lookup: 10.1000/bad'), output.rfind('10.1000/b'))

    def test_rtf_output_uses_one_visible_line_per_entry(self):
        doi_resolver = MagicMock()
        doi_resolver.request.side_effect = [
            {
                'bibtex_type': 'article',
                'author': [{'given': 'Joseph', 'family': 'Barker'}],
                'title': 'Paper One',
                'journal': 'Journal One',
                'journal_abbreviation': 'J. One',
                'volume': '1',
                'pages': ['10'],
                'year': '2024',
                'url': 'https://doi.org/10.1000/one',
            },
            {
                'bibtex_type': 'article',
                'author': [{'given': 'Joseph', 'family': 'Barker'}],
                'title': 'Paper Two',
                'journal': 'Journal Two',
                'journal_abbreviation': 'J. Two',
                'volume': '2',
                'pages': ['20'],
                'year': '2025',
                'url': 'https://doi.org/10.1000/two',
            },
        ]

        with patch('sys.argv', ['blib', '--output', 'rtf', '--no-clip', '10.1000/one', '10.1000/two']), \
             patch('blib.main.blib.providers.CrossrefProvider', return_value=doi_resolver), \
             patch('blib.main.blib.providers.ArxivProvider'), \
             patch('sys.stdout', new_callable=io.StringIO) as stdout:
            main()

        output = stdout.getvalue()

        self.assertIn(r'{\rtf1\ansi\deff0{\colortbl;', output)
        self.assertIn('Paper One', output)
        self.assertIn('Paper Two', output)
        self.assertIn('\\par}\n{\\pard', output)

    def test_rtf_doi_lookup_failures_are_red_paragraphs(self):
        doi_resolver = MagicMock()
        doi_resolver.request.side_effect = URLError('not found')

        with patch('sys.argv', ['blib', '--output', 'rtf', '--no-clip', '10.1000/missing']), \
             patch('blib.main.blib.providers.CrossrefProvider', return_value=doi_resolver), \
             patch('blib.main.blib.providers.ArxivProvider'), \
             patch('sys.stdout', new_callable=io.StringIO) as stdout:
            main()

        output = stdout.getvalue()

        self.assertIn(r'{\rtf1\ansi\deff0{\colortbl;', output)
        self.assertIn(r'{\pard \cf2 // failed DOI lookup: 10.1000/missing \cf0 \par}', output)
