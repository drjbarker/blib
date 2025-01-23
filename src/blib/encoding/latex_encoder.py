import re
import unicodedata
import xml.etree.ElementTree as ET

from pylatexenc.latexencode import UnicodeToLatexEncoder

from blib.encoding.encoder import Encoder


def do_nfkd_escape(text):
    tex_diacritics = {
        rb'\u0300': rb'\u005c\u0060',  # r'\`',  # grave accent
        rb'\u0301': rb'\u005c\u0027',  # r'\'',  # acute accent
        rb'\u0302': rb'\u005c\u005e',  # r'\^',  # circumflex accent
        rb'\u0303': rb'\u005c\u007e',  # r'\~',  # tilde over letter
        rb'\u0304': rb'\u005c\u003d',  # r'\=',  # macron
        rb'\u0306': rb'\u005c\u0075\u0020',  # r'\u ', # breve accent
        rb'\u0307': rb'\u005c\u002e',  # r'\.',  # dot accent
        rb'\u0308': rb'\u005c\u0022',  # r'\"',  # diaeresis (umlaut)
        rb'\u030a': rb'\u005c\u0072\u0020',  # r'\r '  # ring above
        rb'\u030b': rb'\u005c\u0048\u0020',  # r'\H ', # long Hungarian umlaut (double acute accent)
        rb'\u030c': rb'\u005c\u0076\u0020',  # r'\v ', # caron (hacek)
        rb'\u0323': rb'\u005c\u0064\u0020',  # r'\d ', # dot-under accent
        rb'\u0327': rb'\u005c\u0063\u0020',  # r'\c ', # cedilla
        rb'\u0328': rb'\u005c\u006b\u0020',  # r'\k ', # ogonek
        rb'\u0331': rb'\u005c\u0062\u0020',  # r'\b ', # bar-under accent
        rb'\u0361': rb'\u005c\u0074\u0020',  # r'\t ', # double inverted breve (tie)
    }

    # encode to unicode escaped byte string decomposition characters
    byte_string = unicodedata.normalize('NFKD', text).encode('unicode-escape')

    # loop through all diacritics and attempt a substitution in the string
    for unicode_dia, tex_dia in tex_diacritics.items():
        regex = re.compile(b'([a-zA-Z])' + re.escape(unicode_dia))
        byte_string = regex.sub(b'{' + re.escape(tex_dia) + b'\g<1>}', byte_string)

    return byte_string.decode('unicode-escape')

def is_ascii(string):
    """
    Returns true if the string only contains ASCII characters,
    False otherwise.
    """
    try:
        string.encode('ascii')
    except UnicodeEncodeError:
        return False
    return True

class LatexEncoder(Encoder):

    def __init__(self, default_latex_textstyle="none", autoformat_chemical_formulae=True):
        self._pylatexenc = UnicodeToLatexEncoder(replacement_latex_protection='braces-all', unknown_char_policy='fail')
        self._default_latex_textstyle = default_latex_textstyle
        self._autoformat_chemical_formulae = autoformat_chemical_formulae

    def _translate_unicode_to_latex(self, text):
        return self._pylatexenc.unicode_to_latex(text)

    def _encode_text(self, text):
        try:
            return self._pylatexenc.unicode_to_latex(text)
        except ValueError:
            # TODO: the ValueError will be raised on the first character
            # with an issue and stop unicode_to_latex from processing the
            # rest of the string. Ideally we want to try to fix one character
            # then continue with unicode_to_latex.
            return do_nfkd_escape(text)

    def encode_word(self, text):
        return f'{self._encode_text(text)}'

    def encode_noun(self, text):
        return f'{{{self._encode_text(text)}}}'

    def encode_whitespace(self, text):
        return f' '

    def encode_punctuation(self, text):
        return self._pylatexenc.unicode_to_latex(text)

    def encode_unicode_math(self, text):
        return f'${self._encode_text(text)}$'

    def encode_symbol(self, text):
        return f'{self._encode_text(text)}'

    def encode_chemical(self, text):
        # If the encoder is set to autoformat chemical formulae then typeset numbers as subscripts. If the option
        # is off then simply return the string.
        if self._autoformat_chemical_formulae:

            formula_search = re.search(self._token_regex_chemical, text)
            if formula_search:
                elements = formula_search.group(1)
                subscript = formula_search.group(2)
                return f'{{{elements}$_{{{self._encode_text(subscript)}}}$}}'
        return text

    def encode_html_sub(self, node):
        return f'$_{{{self._encode_text(node.text)}}}$'

    def encode_html_sup(self, node):
        return f'$^{{{self._encode_text(node.text)}}}$'

    def encode_html_b(self, node):
        return rf'\textbf{{{self._encode_text(node.text)}}}'

    def encode_html_i(self, node):
        return rf'\textit{{{self._encode_text(node.text)}}}'

    def encode_html_tt(self, node):
        return rf'\texttt{{{self._encode_text(node.text)}}}'

    def _get_mathml_latex_textstyle(self, elem):
        mapping = {
            "none": r"",
            "normal": r"\mathrm",
            "bold": r"\mathbf",
            "italic": r"\mathit",
            "double-struck": r"\mathbb",
            "script": r"\mathscr",
            "fraktur": r"\mathfrak",  # requires eufrak
        }
        if "mathvariant" in elem.attrib:
            if elem.attrib["mathvariant"] in mapping:
                return mapping[elem.attrib["mathvariant"]]
        return mapping[self._default_latex_textstyle]

    def encode_mathml(self, text):
        return f"{{${self._walk_mathml_tree(ET.fromstring(text))}$}}"

    def encode_mathml_mtext(self, node):
        if self._get_mathml_latex_textstyle(node):
            return rf'{self._get_mathml_latex_textstyle(node)}{{{self._pylatexenc.unicode_to_latex(node.text)}}}'
        return self._pylatexenc.unicode_to_latex(node.text)

    def encode_mathml_mi(self, node):
        # sometimes we will have an empty tag like <mml:mi mathvariant="italic" /> which contains no text
        # this seems to represent a space in some places (e.g. 10.1103/physrevlett.75.729) so we will do
        # the same
        if not node.text:
            return r"\ "
        if self._get_mathml_latex_textstyle(node):
            return rf'{self._get_mathml_latex_textstyle(node)}{{{self._pylatexenc.unicode_to_latex(node.text)}}}'
        return self._pylatexenc.unicode_to_latex(node.text)

    def encode_mathml_mn(self, node):
        return self._pylatexenc.unicode_to_latex(node.text)

    def encode_mathml_mo(self, node):
        return self._pylatexenc.unicode_to_latex(node.text)

    def encode_mathml_msub(self, node):
        # <msub> base subscript </msub>
        base, subscript = node
        return rf'{{{self._walk_mathml_tree(base)}}}_{{{self._walk_mathml_tree(subscript)}}}'

    def encode_mathml_msup(self, node):
        # <msub> base subscript </msub>
        base, subscript = node
        return rf'{{{self._walk_mathml_tree(base)}}}^{{{self._walk_mathml_tree(subscript)}}}'


