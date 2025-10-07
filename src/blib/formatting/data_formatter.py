from collections import OrderedDict

import blib.encoding
from blib.citekey import article_citekey, misc_citekey
from blib.encoding import UnicodeEncoder
from blib.formatting.formatter import Formatter
from blib.utils import flatten


class DataFormatter(Formatter):

    def __init__(self,
                 abbreviate_journals=True):
        self._encoder = UnicodeEncoder()
        self._abbreviate_journals = abbreviate_journals

    def format(self, data):

        fields = self._format(data)

        return '\n'.join([f'{key}\t{value}' for key, value in fields.items()])

    def _format(self, data):
        # We don't use a dictionary here because we want the printing to be ordered and deterministic
        fields = OrderedDict()
        fields["author"] = self._authors(data["authors"])
        fields["title"] = self._encoder.encode(data["title"], nouns=True, chemicals=True)

        if "journal-abbrev" in data and self._abbreviate_journals:
            fields["journal"] = self._encoder.encode(data["journal-abbrev"])
        elif "journal" in data:
            fields["journal"] = self._encoder.encode(data["journal"])

        if "issue" in data and data["issue"]:
            fields["issue"] = data["issue"]

        if "volume" in data and data["volume"]:
            fields["volume"] = data["volume"]

        if "pages" in data:
            if data["pages"] is None:
                pass
            elif len(data["pages"]) == 1:
                fields["pages"] = data["pages"][0]
            elif len(data["pages"]) == 2:
                fields["pages"] = f'{data["pages"][0]}--{data["pages"][1]}'

        fields["year"] = data["published-date"]["year"]

        if "month" in data["published-date"] and data["published-date"]["month"]:
            fields["month"] = data["published-date"]["month"]

        if "publisher" in data and data["publisher"]:
            fields["publisher"] = self._encoder.encode(data["publisher"])

        if "doi" in data:
            fields["doi"] = data["doi"]

        if "url" in data:
            fields["url"] = data["url"]

        return fields

    def _authors(self, author_list):
        result = []
        for author in author_list:
            # Some sources seem to use lists for given names (e.g. 10.1109/LED.2008.2012270).
            # Presumably this allows middle names to be expressed. Therefore we flatten the
            # given names into a single string.
            result.append(f'{self._encoder.encode(author["family"])}, {self._encoder.encode(flatten(author["given"]))}')
        return ' and '.join(result)
