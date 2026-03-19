from unittest import TestCase
from unittest.mock import Mock

from blib.main import find_arxiv_id_from_doi, resolve_resource_data
from blib.resourceid import ResourceId, ResourceIdType


class MainTest(TestCase):
    def test_find_arxiv_id_from_doi_returns_arxiv_resource(self):
        resource_id = find_arxiv_id_from_doi("10.48550/arXiv.2603.08777")

        self.assertEqual(resource_id, ResourceId("2603.08777", ResourceIdType.arxiv))

    def test_resolve_resource_data_uses_arxiv_provider_for_arxiv_doi(self):
        doi_resolver = Mock()
        arxiv_resolver = Mock()
        arxiv_resolver.request.return_value = {"entry": "misc", "eprint": "2603.08777"}

        result = resolve_resource_data(
            ResourceId("10.48550/arXiv.2603.08777", ResourceIdType.doi),
            doi_resolver,
            arxiv_resolver,
        )

        self.assertEqual(result, {"entry": "misc", "eprint": "2603.08777"})
        doi_resolver.request.assert_not_called()
        arxiv_resolver.request.assert_called_once_with("2603.08777")
