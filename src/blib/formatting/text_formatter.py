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

        result.append(self._journal(data))
        result.append(self._citation_details(data))

        return ''.join(result)

    def _journal(self, data):
        if self._abbreviate_journals and data.get("journal-abbrev"):
            return self._encoder.encode(data["journal-abbrev"])
        return self._encoder.encode(data["journal"])

    def _citation_details(self, data):
        details = []

        if data.get("volume"):
            details.append(str(data["volume"]))

        pages = self._pages(data)
        if pages:
            details.append(pages)

        year = data["published-date"]["year"]

        if details:
            return f" {', '.join(details)} ({year})"
        return f" ({year})"

    def _pages(self, data):
        if "pages" not in data or data["pages"] is None:
            return None

        try:
            return data["pages"][0]
        except TypeError:
            return data["pages"]

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
