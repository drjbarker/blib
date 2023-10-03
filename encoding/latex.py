from .encoder import Encoder
import unicodedata

from encoding.tokenizer import chemical_formula_regex

import re
import xml.etree.ElementTree as ET

from pylatexenc.latexencode import UnicodeToLatexEncoder

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
        self._pylatexenc = UnicodeToLatexEncoder(replacement_latex_protection='braces-all')
        self._default_latex_textstyle = default_latex_textstyle
        self._autoformat_chemical_formulae = autoformat_chemical_formulae

    def _translate_unicode_to_latex(self, text):
        return self._pylatexenc.unicode_to_latex(text)

    def _encode_text(self, text):
        return self._pylatexenc.unicode_to_latex(text)

    def encode_word(self, text):
        return f'{self._encode_text(text)}'

    def encode_noun(self, text):
        return f'{{{self._encode_text(text)}}}'

    def encode_whitespace(self, text):
        return f' '

    def encode_punctuation(self, text):
        return text

    def encode_unicode_math(self, text):
        return f'${self._encode_text(text)}$'

    def encode_chemical(self, text):
        # If the encoder is set to autoformat chemical formulae then typeset numbers as subscripts. If the option
        # is off then simply return the string.
        if self._autoformat_chemical_formulae:
            return re.sub(chemical_formula_regex, r'{\g<1>}$_{\g<2>}$', text)
        return text

    def encode_html_sub(self, node):
        return f'$_{{{self._encode_text(node.text)}}}$'

    def encode_html_sup(self, node):
        return f'$^{{{self._encode_text(node.text)}}}$'

    def encode_html_b(self, node):
        return rf'\textbf{{{self._encode_text(node.text)}}}'

    def encode_html_i(self, node):
        return rf'\textit{{{self._encode_text(node.text)}}}'

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
        return f"${self._walk_mathml_tree(ET.fromstring(text))}$"

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


