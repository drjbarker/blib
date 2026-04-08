from unittest import TestCase

from blib.formatting.markdown import MarkdownFormatter
from blib.formatting.text_formatter import TextFormatter


class FormatterTest(TestCase):
    def test_text_formatter_handles_misc_entries_without_volume_or_pages(self):
        formatter = TextFormatter(use_title=True)

        data = {
            "entry": "misc",
            "authors": [{"given": "Ada", "family": "Lovelace"}],
            "title": "Notes on the Analytical Engine",
            "journal": "arXiv.2603.08777v1 [cs.LG]",
            "url": "https://arxiv.org/abs/2603.08777v1",
            "published-date": {"year": 2026, "month": 3},
            "eprint": "2603.08777v1",
        }

        self.assertEqual(
            formatter.format(data),
            "A. Lovelace, Notes on the Analytical Engine, arXiv.2603.08777v1 [cs.LG] (2026)",
        )

    def test_markdown_formatter_handles_misc_entries_without_journal_abbrev_or_volume(self):
        formatter = MarkdownFormatter(use_title=True)

        data = {
            "entry": "misc",
            "authors": [{"given": "Ada", "family": "Lovelace"}],
            "title": "Notes on the Analytical Engine",
            "journal": "arXiv.2603.08777v1 [cs.LG]",
            "url": "https://arxiv.org/abs/2603.08777v1",
            "published-date": {"year": 2026, "month": 3},
            "eprint": "2603.08777v1",
        }

        self.assertEqual(
            formatter.format(data),
            "[#Lovelace_2603_08777v1_2026]: A. Lovelace, *Notes on the Analytical Engine*, "
            "[arXiv.2603.08777v1 [cs.LG] (2026)](https://arxiv.org/abs/2603.08777v1)",
        )
