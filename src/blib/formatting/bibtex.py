from collections import OrderedDict

import blib.encoding
from blib.citekey import article_citekey, misc_citekey
from blib.formatting.formatter import Formatter
from blib.utils import flatten


class BibtexFormatter(Formatter):

    def __init__(self,
                 abbreviate_journals=True):
        self._encoder = blib.encoding.LatexEncoder()
        self._abbreviate_journals = abbreviate_journals

    def format(self, data):

        if data['entry'] == 'article':
            citekey, fields = self._format_article(data)
        else:
            citekey, fields = self._format_misc(data)

        fields = ',\n'.join([f'  {key:9} = {{{value}}}' for key, value in fields.items()])

        return (
            f"@{data['entry']}{{{citekey},\n"
            f"{fields}\n"
            f"}}\n"
        )

    def _format_article(self, data):
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

        return article_citekey(data), fields

    def _format_misc(self, data):

        standard_fields = ("entry", "authors", "title", "journal-abbrev", "journal", "issue", "volume",
                           "pages", "published-date", "publisher", "doi", "url", "eprint")

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
        fields["month"] = data["published-date"]["month"]

        if "publisher" in data and data["publisher"]:
            fields["publisher"] = self._encoder.encode(data["publisher"])

        if "eprint" in data and data["eprint"]:
            fields["eprint"] = data["eprint"]

        for key, value in data.items():
            if key not in standard_fields:
                fields[key] = value

        if "doi" in data:
            fields["doi"] = data["doi"]

        if "url" in data:
            fields["url"] = data["url"]

        return misc_citekey(data), fields


    def _authors(self, author_list):
        result = []
        for author in author_list:
            # Some sources seem to use lists for given names (e.g. 10.1109/LED.2008.2012270).
            # Presumably this allows middle names to be expressed. Therefore we flatten the
            # given names into a single string.
            result.append(f'{self._encoder.encode(author["family"])}, {self._encoder.encode(flatten(author["given"]))}')
        return ' and '.join(result)

# from sources.crossref import CrossrefSource
#
# formatter = BibtexFormatter()
# source = CrossrefSource()
# print(formatter.format(
#     source.request('10.1103/physrev.130.1677')))