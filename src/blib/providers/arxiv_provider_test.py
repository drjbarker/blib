from unittest import TestCase

import blib.providers


class TestArxivSource(TestCase):
    def test_request(self):
        source = blib.providers.ArxivProvider()

        print(source.request('2310.03169'))
