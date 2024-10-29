from unittest import TestCase
from .crossref import CrossrefSource

class TestCrossrefSource(TestCase):
    def test_request(self):
        source = CrossrefSource()

        print(source.request('10.1002/adma.202302419'))
