from blib.citekey import article_citekey, misc_citekey
from blib.encoding.unicode_encoder import UnicodeEncoder
from blib.formatting.bibdesk_autogeneration import BibDeskAutogenerationFormatter
from .formatter import Formatter


class MarkdownFormatter(Formatter):

    def __init__(self,
                 abbreviate_journals=True,
                 use_title=False,
                 max_authors=1,
                 etal="et al.",
                 format_string=None):
        self._encoder = UnicodeEncoder()
        self._abbreviate_journals = abbreviate_journals
        self._use_title = use_title
        self._max_authors = max_authors
        self._etal = etal
        self._format_string = format_string
        self._bibdesk_formatter = None
        if format_string:
            self._bibdesk_formatter = BibDeskAutogenerationFormatter(format_string, self._encoder)

    def format(self, data):
        if self._bibdesk_formatter:
            return self._bibdesk_formatter.format(data)

        result = []

        if data['bibtex_type'] == 'article':
            citekey = article_citekey(data)
        else:
            citekey = misc_citekey(data)

        result.append(f"[#{citekey}]: ")

        authors = self._authors(data['author'])

        if authors:
            result.append(f"{self._authors(data['author'])}, ")

        if self._use_title:
            result.append(f"*{self._encoder.encode(data['title'])}*, ")

        result.append("[")

        if self._abbreviate_journals:
            result.append(f"{self._encoder.encode(data['journal_abbreviation'])}")
        else:
            result.append(f"{self._encoder.encode(data['journal'])}")

        try:
            pages = data['pages'][0]
        except TypeError:
            pages = data['pages']

        result.append(f" **{data['volume']}**, {pages} ({data['year']})")
        result.append(f"]({data['url']})")

        return ''.join(result)

    def _abbreviate_authors(self, given_name):
        abbrev_list = []
        for name in given_name.split(" "):
            if name[-1] == ".":
                abbrev_list.append(name[:-1])
            else:
                abbrev_list.append(name[0])

        return f'{".".join(abbrev_list)}.'

        # deal with hyphens as von-Kim -> v.-K.

    def _authors(self, author_list):

        if self._max_authors == 0:
            return ""

        used_authors = author_list[0:self._max_authors]

        if len(author_list) == 1:
            return f'{self._encoder.encode(self._abbreviate_authors(used_authors[0]["given"]))} {self._encoder.encode(used_authors[0]["family"])}'

        result = []
        for author in used_authors[:-1]:
            result.append(
                f'{self._encoder.encode(self._abbreviate_authors(author["given"]))} {self._encoder.encode(author["family"])}, ')

        if len(author_list) == len(used_authors):
            # all authors are used so the last entry is included with '&'
            result.append(
                f'and {self._encoder.encode(self._abbreviate_authors(used_authors[-1]["given"]))} {self._encoder.encode(used_authors[-1]["family"])}')
        else:
            # a truncated author list is used so finish with 'et al.'
            result.append(
                f'{self._encoder.encode(self._abbreviate_authors(used_authors[-1]["given"]))} {self._encoder.encode(used_authors[-1]["family"])}')

            if self._etal:
                result.append(f" {self._etal}")


        return f"{''.join(result)}"
