from unittest import TestCase

import blib.providers


class TestCrossrefSource(TestCase):
    def test_request(self):
        source = blib.providers.CrossrefProvider()

        print(source.request('10.1002/adma.202302419'))
