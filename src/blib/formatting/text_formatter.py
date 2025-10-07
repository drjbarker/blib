from blib.encoding.unicode_encoder import UnicodeEncoder
from blib.formatting.formatter import Formatter


class TextFormatter(Formatter):

    def __init__(self,
                 abbreviate_journals=True,
                 use_title=False,
                 max_authors=1,
                 etal="et al."):
        self._encoder = UnicodeEncoder()
        self._abbreviate_journals = abbreviate_journals
        self._use_title = use_title
        self._max_authors = max_authors
        self._etal = etal

    def format(self, data):

        result = []

        authors = self._authors(data['authors'])

        if authors:
            result.append(f"{self._authors(data['authors'])}, ")

        if self._use_title:
            result.append(f"{self._encoder.encode(data['title'])}, ")

        if self._abbreviate_journals:
            result.append(f"{self._encoder.encode(data['journal-abbrev'])}")
        else:
            result.append(f"{self._encoder.encode(data['journal'])}")

        try:
            pages = data['pages'][0]
        except TypeError:
            pages = data['pages']

        result.append(f" {data['volume']}, {pages} ({data['published-date']['year']})")

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
