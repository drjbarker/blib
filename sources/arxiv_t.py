from unittest import TestCase
from .arxiv import ArxivSource

class TestArxivSource(TestCase):
    def test_request(self):
        source = ArxivSource()

        print(source.request('2310.03169'))
