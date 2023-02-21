from .encoder import Encoder
import unicodedata

from types import MappingProxyType
from encoding.tokenizer import chemical_formula_regex

import re
import xml.etree.ElementTree as ET

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

unicode_math_to_latex = MappingProxyType({
    # Complex numbers
    'ℑ': r'\Im',
    'ℜ': r'\Re',

    # Elementary arithmetic operations
    '⋅': r'\cdot',
    '⨯': r'\times',
    '−': r'-',
    '+': r'+',
    '±': r'\pm',
    '∓': r'\mp',
    '∕': r'/',
    '∗': r'*',

    # Elementary functions
    '√': r'\sqrt',
    '∛': r'\sqrt[3]',
    '∜': r'\sqrt[4]',
    '%': r'\%',
    '{': r'\{',
    '}': r'\}',
    '⌈': r'\lceil',
    '⌉': r'\rceil',
    '⌊': r'\lfloor',
    '⌋': r'\rfloor',
    '⌜': r'\ulcorner',
    '⌝': r'\urcorner',
    '⌞': r'\llcorner',
    '⌟': r'\lrcorner',
    '⌢': r'\frown',
    '⌣': r'\smile',

    # Arithmetic comparison
    '<': r'<',
    '>': r'>',
    '≤': r'\leq',
    '≥': r'\geq',
    '≦': r'\leqq',
    '≧': r'\geqq',
    '⩽': r'\leqslant',
    '⩾': r'\geqslant',
    '≪': r'\ll',
    '≫': r'\gg',
    '≲': r'\lesssim',
    '≳': r'\gtrsim',
    '⪅': r'\lessapprox',
    '⪆': r'\gtrapprox',
    '≶': r'\lessgtr',
    '≷': r'\gtrless',
    '⋚': r'\lesseqgtr',
    '⋛': r'\gtreqless',
    '⪋': r'\lesseqqgtr',
    '⪌': r'\gtreqqless',

    # Divisibility and modulo
    '∣': r'\mid',
    '∤': r'\nmid',
    '⊥': r'\perp',
    '⊓': r'\sqcap',
    '∧': r'\wedge',
    '⊔': r'\sqcup',
    '∨': r'\vee',
    '≡': r'\equiv',

    # Combinatorics
    '#': r'\#',

    # Probability theory
    '≈': r'\approx',

    # Statistics
    '⟨': r'\langle',
    '⟩': r'\rangle',

    # Sequences and series
    '∑': r'\sum',
    '∏': r'\prod',
    '∐': r'\coprod',
    '→': r'\to',

    ' ': r' ',
    '∀': r'\forall',
    '∁': r'\complement',
    '∂': r'\partial',
    '∃': r'\exists',
    '∄': r'\nexists',
    '∅': r'\emptyset',
    '∆': r'\Delta',
    '∇': r'\nabla',
    '∈': r'\in',
    '∉': r'\notin',
    '∊': r'\in',
    '∋': r'\ni',
    '∌': r'\notni',
    '∍': r'\ni',
    '∎': r'\blacksquare',

    '∝': r'\propto',
    '∞': r'\infty',
    '∫': r'\int',
    '∬': r'\iint',
    '∭': r'\iiint',
    '∮': r'\oint',
    '∯': r'oiint',
    '∰': r'oiiint',
    '∴': r'\therefore',
    '∵': r'\because',
    '∶': r':',
    '∼': r'\sim',

    'ⅆ': r'd',

    'α': r'\alpha',
    'β': r'\beta',
    'γ': r'\gamma',
    'δ': r'\delta',
    'Δ': r'\Delta',
    'ε': r'\varepsilon',
    'ζ': r'\zeta',
    'η': r'\eta',
    'θ': r'\theta',
    'ϑ': r'\vartheta',
    'Θ': r'\Theta',
    'ι': r'\iota',
    'κ': r'\kappa',
    'λ': r'\lambda',
    'Λ': r'\Lambda',
    'μ': r'\mu',
    'ν': r'\nu',
    'ξ': r'\xi',
    'Ξ': r'\Xi',
    'π': r'\pi',
    'Π': r'\Pi',
    'ρ': r'\rho',
    'ϱ': r'\varrho',
    'σ': r'\sigma',
    'Σ': r'\Sigma',
    'τ': r'\tau',
    'υ': r'\upsilon',
    'ϒ': r'\Upsilon',
    'ϕ': r'\phi',
    'φ': r'\varphi',
    'Φ': r'\Phi',
    'χ': r'\chi',
    'ψ': r'\psi',
    'Ψ': r'\Psi',
    'ω': r'\omega',
    'Ω': r'\Omega',
})

class LatexEncoder(Encoder):

    def __init__(self, default_latex_textstyle="none", autoformat_chemical_formulae=True):
        self._default_latex_textstyle = default_latex_textstyle
        self._autoformat_chemical_formulae = autoformat_chemical_formulae

    _unicode_translation = str.maketrans(dict(unicode_math_to_latex))

    def _translate_unicode_to_latex(self, text):
        return text.translate(self._unicode_translation)

    def _encode_text(self, text):
        return self._encode_diacritics(self._translate_unicode_to_latex(text))

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
            return rf'{self._get_mathml_latex_textstyle(node)}{{{node.text.translate(self._unicode_translation)}}}'
        return node.text.translate(self._unicode_translation)

    def encode_mathml_mi(self, node):
        # sometimes we will have an empty tag like <mml:mi mathvariant="italic" /> which contains no text
        # this seems to represent a space in some places (e.g. 10.1103/physrevlett.75.729) so we will do
        # the same
        if not node.text:
            return r"\ "
        if self._get_mathml_latex_textstyle(node):
            return rf'{self._get_mathml_latex_textstyle(node)}{{{node.text.translate(self._unicode_translation)}}}'
        return node.text.translate(self._unicode_translation)

    def encode_mathml_mn(self, node):
        return node.text.translate(self._unicode_translation)

    def encode_mathml_mo(self, node):
        return node.text.translate(self._unicode_translation)

    def encode_mathml_msub(self, node):
        # <msub> base subscript </msub>
        base, subscript = node
        return rf'{{{self._walk_mathml_tree(base)}}}_{{{self._walk_mathml_tree(subscript)}}}'

    def encode_mathml_msup(self, node):
        # <msub> base subscript </msub>
        base, subscript = node
        return rf'{{{self._walk_mathml_tree(base)}}}^{{{self._walk_mathml_tree(subscript)}}}'

    def _encode_diacritics(self, text):
        """Replaces unicode diacritics with tex escaped diacritics and returns the escaped string.

           Our definition of a diacritic (instead of a special character) is that it modifies a character. In general it
           will have a syntax like {\'a} where 'a' is the character being modified.

           The returned string is NOT guaranteed to contain only ascii ordinals. We only escape the unicode diacritics, all
           other unicode characters are unchanged.

           Technical Details
           -----------------
           The unicode tex is normalized using the NFKD scheme. The 'D' stands for decomposition which means characters
           which can be composed of multiple sub-symbols (like diacritics) are split into those sub-symbols. For example
           à will be split into the unicode symbols 'Combining Grave Accent (U+0300)' and 'Latin Small Letter A (U+0061)'.
           If we use an alternative normalisation which does not decompose then we would get 'Latin Small Letter a with
           Grave (U+00E0)'. Tex syntax for diacritics is very similar to the unicode decomposition, i.e. it is a combining
           charater and a modified letter and so it is a natural way to convert. If we do not do the decomposition then we
           would have to write the diacritic for every possible diacritical letter.

           In the tex escaped string curley braces are used on the outside of the sequence {\`a}, not around the modified
           character (\`{a}). Both are valid tex, but the {\`a} syntax can be used by bibtex for alphabetical sorting in
           languages where diacritic characters may not be inorder of the 'base' character which is being modified
           (see https://tex.stackexchange.com/a/57745).

           In at least one case (å -> \{r a} or {\aa}) there is both a diacritic and a special character equivalent for the
           letter. We allow the diacritic version to be converted here.
        """
        # if the string is pure ascii then there is nothing to encode into tex
        if is_ascii(text):
            return text

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


