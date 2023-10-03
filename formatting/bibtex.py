import itertools

from .formatter import Formatter
from encoding.latex import LatexEncoder
import unicodedata
from collections import OrderedDict

try:
    from unidecode import unidecode
    has_unidecode = True
except:
    has_unidecode = False

def normalise_unicode_to_ascii(string):
    """
    Removes any non-ascii characters from the string, replacing them with latin equivalents if possible
    """
    if has_unidecode:
        return unidecode(string)
    else:
        return unicodedata.normalize('NFKD', string).encode('ascii', 'ignore').decode()

def flatten(x):
    """
    Flattens an iteratable object into a string
    """
    if isinstance(x, str):
        return x

    return ''.join(itertools.chain.from_iterable(x))

class BibtexFormatter(Formatter):

    def __init__(self,
                 abbreviate_journals=True):
        self._encoder = LatexEncoder()
        self._abbreviate_journals = abbreviate_journals

    def format(self, data):

        # We don't use a dictionary here because we want the printing to be ordered and deterministic
        fields = OrderedDict()
        fields["author"] = self._authors(data["authors"])
        fields["title"] = self._encoder.encode(data["title"], nouns=True)

        if self._abbreviate_journals:
            fields["journal"] = self._encoder.encode(data["journal-abbrev"])
        else:
            fields["journal"] = self._encoder.encode(data["journal"])

        if data["issue"]:
            fields["issue"] = data["issue"]

        if data["volume"]:
            fields["volume"] = data["volume"]

        if data["pages"] is None:
            pass
        elif len(data["pages"]) == 1:
            fields["pages"] = data["pages"][0]
        elif len(data["pages"]) == 2:
            fields["pages"] = f'{data["pages"][0]}--{data["pages"][1]}'

        fields["year"] = data["published-date"]["year"]
        fields["month"] = data["published-date"]["month"]

        if data["publisher"]:
            fields["publisher"] = self._encoder.encode(data["publisher"])

        fields["doi"] = data["doi"]
        fields["url"] = data["url"]

        fields = ',\n'.join([f'  {key:9} = {{{value}}}' for key, value in fields.items()])

        return (
            f"@{data['entry']}{{{self._citekey(data)},\n"
            f"{fields}\n"
            f"}}\n"
        )

    def _citekey(self, data):
        author = normalise_unicode_to_ascii(data['authors'][0]['family']).replace(' ', '').replace('-', '')
        journal = data['journal-abbrev'].replace(' ', '').replace('.', '').replace(':', '')
        if data["pages"] is None:
            return f'{author}_{journal}_{data["volume"]}_{data["published-date"]["year"]}'
        return f'{author}_{journal}_{data["volume"]}_{data["pages"][0]}_{data["published-date"]["year"]}'

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