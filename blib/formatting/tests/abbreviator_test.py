from unittest import TestCase

from blib.formatting import abbreviator

class AbbreviatorTest(TestCase):
    """Tests the Abbreviator class."""

    def test_abbreviator(self):
        parser = abbreviator.Abbreviator()

        parser.insert('Test\S*', 'T')

        self.assertEqual(parser.abbreviate('Test'), 'T')
        self.assertEqual(parser.abbreviate('Testing'), 'T')

        parser.insert('of', '')

        self.assertEqual(parser.abbreviate('Testing of'), 'T')
