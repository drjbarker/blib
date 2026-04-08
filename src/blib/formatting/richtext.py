import blib.encoding
from blib.formatting.bibdesk_autogeneration import BibDeskAutogenerationFormatter
from blib.formatting.text_formatter import TextFormatter


class RichTextFormatter(TextFormatter):

    def __init__(self,
                 abbreviate_journals=True,
                 use_title=False,
                 max_authors=1,
                 etal="et al.",
                 format_string=None):
        TextFormatter.__init__(self,
                               abbreviate_journals=abbreviate_journals,
                               use_title=use_title,
                               max_authors=max_authors,
                               etal=f"\i {etal}\i0" if etal else "",
                               format_string=format_string)
        self._encoder = blib.encoding.RichTextEncoder()
        if format_string:
            self._bibdesk_formatter = BibDeskAutogenerationFormatter(format_string, self._encoder)

    def format(self, data):
        if self._bibdesk_formatter:
            citation = self._bibdesk_formatter.format(data)
            return rf'{{\pard {citation} \par}}'

        if data['bibtex_type'] == 'article':
            return self._format_article(data)
        else:
            return self._format_misc(data)

    def _format_article(self, data):
        result = []

        authors = self._authors(data['author'])

        if authors:
            result.append(f"{self._authors(data['author'])}, ")

        if self._use_title:
            result.append(f"{self._encoder.encode(data['title'])}, ")

        if "url" in data:
            result.append(rf'{{\field{{\*\fldinst HYPERLINK "{data["url"]}"}}{{\fldrslt{{\ul\cf1')

        if self._abbreviate_journals:
            result.append(f"{self._encoder.encode(data['journal_abbreviation'])}")
        else:
            result.append(f"{self._encoder.encode(data['journal'])}")

        result.append(f" \\b {data['volume']}\\b0")

        if data['pages']:
            result.append(f", {data['pages'][0]} ")
        else:
            result.append(f"  ")

        result.append(f"({data['year']})")

        if "url" in data:
            result.append('}}}')

        citation = ''.join(result)
        return rf'{{\pard {citation} \par}}'

    def _format_misc(self, data):

        result = []

        authors = self._authors(data['author'])

        if authors:
            result.append(f"{self._authors(data['author'])}, ")

        if self._use_title:
            result.append(f"{self._encoder.encode(data['title'])}, ")

        if "url" in data:
            result.append(rf'{{\field{{\*\fldinst HYPERLINK "{data["url"]}"}}{{\fldrslt{{\ul\cf1')

        if "journal_abbreviation" in data and self._abbreviate_journals:
            result.append(f"{self._encoder.encode(data['journal_abbreviation'])}")
        elif "journal" in data:
            result.append(f"{self._encoder.encode(data['journal'])}")

        if "volume" in data:
            result.append(f" \\b {data['volume']}\\b0")

        if "pages" in data:
            if data['pages'] is None:
                pass
            elif len(data['pages']) == 1:
                result.append(f", {data['pages'][0]} ")
            elif len(data['pages']) == 2:
                result.append(f", {data['pages'][0]}--{data['pages'][1]} ")
        else:
            result.append(f"  ")

        result.append(f"({data['year']})")

        if "url" in data:
            result.append('}}}')

        citation = ''.join('')

        return rf'{{\pard {citation} \par}}'


    def header(self):
        return r'{\rtf1\ansi\deff0{\colortbl;\red0\green0\blue255;\red255\green0\blue0;} '

    def footer(self):
        return r'}'
