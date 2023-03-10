import xml.etree.ElementTree as ET
import re

# xml_text=r'<mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML"><mml:mrow><mml:msub><mml:mi>MnBi</mml:mi><mml:mn>2</mml:mn></mml:msub><mml:msub><mml:mi>Te</mml:mi><mml:mn>4</mml:mn></mml:msub></mml:mrow></mml:math>'

# xml_text=r'<mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML" display="inline"><mml:mrow><mml:mi>G</mml:mi><mml:mi>W</mml:mi></mml:mrow></mml:math>'
# xml_text=r'<mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML" display="inline"><mml:mrow><mml:mn>4</mml:mn><mml:mi>f</mml:mi></mml:mrow></mml:math>'

# xml_text=r'<mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML"><mml:msub><mml:mi>SrRuO</mml:mi><mml:mn>3</mml:mn></mml:msub></mml:math>'
xml_text=r'''<math xmlns="http://www.w3.org/1998/Math/MathML" display="block">
  <mi>x</mi> <mo>=</mo>
  <mrow>
    <mfrac>
      <mrow>
        <mo>−</mo>
        <mi>b</mi>
        <mo>±</mo>
        <msqrt>
          <msup><mi>b</mi><mn>2</mn></msup>
          <mo>−</mo>
          <mn>4</mn><mi>a</mi><mi>c</mi>
        </msqrt>
      </mrow>
      <mrow> <mn>2</mn><mi>a</mi> </mrow>
    </mfrac>
  </mrow>
  <mtext>.</mtext>
</math>'''

# xml_text=r'''<math xmlns='http://www.w3.org/1998/Math/MathML'>
#  <mrow>
#   <munderover>
#    <mo>&#8719;</mo>
#    <mrow>
#     <mi>n</mi>
#     <mo>=</mo>
#     <mn>0</mn>
#    </mrow>
#    <mi>&#8734;</mi>
#   </munderover>
#   <mi>n</mi>
#  </mrow>
# </math>'''

# xml_text=r'<mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML" display="inline"><mml:mo>[</mml:mo><mml:mi mathvariant="normal">La</mml:mi><mml:mo>,</mml:mo><mml:mi> </mml:mi><mml:mi>M</mml:mi><mml:mo>(</mml:mo><mml:mi mathvariant="normal">II</mml:mi><mml:mo>)</mml:mo><mml:mo>]</mml:mo><mml:mi mathvariant="normal">Mn</mml:mi><mml:mrow><mml:msub><mml:mrow><mml:mi mathvariant="normal">O</mml:mi></mml:mrow><mml:mrow><mml:mn>3</mml:mn></mml:mrow></mml:msub></mml:mrow></mml:math>'

root = ET.fromstring(xml_text)


def emmit_mi(root):
    return rf'\mathrm{{{root.text}}}'

HANDLERS = {
    '{http://www.w3.org/1998/Math/MathML}mi': emmit_mi
}

# https://www.w3schools.com/charsets/ref_utf_math.asp
# https://en.wikipedia.org/wiki/List_of_mathematical_symbols_by_subject
# https://www.w3.org/TR/MathML3/appendixc.html
UNICODE2TEX = {
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
    'γ': r'\gamma',
    'π': r'\pi',

}

def unicode2tex(text):
    if text in UNICODE2TEX:
        return UNICODE2TEX[text]
    return text


def get_latex_textstyle(elem):
    mapping = {
        "normal": r"\mathrm",
        "bold": r"\mathbf",
        "italic": r"\mathit",
        "double-struck": r"\mathbb",
        "script": r"\mathscr",
        "fraktur": r"\mathfrak", # requires eufrak
    }
    if "mathvariant" in elem.attrib:
        if elem.attrib["mathvariant"] in mapping:
            return mapping[elem.attrib["mathvariant"]]

    # It's basically arbitrary what to choose as the fallback. For typesetting titles
    # often no mathvariant is given but we are typesetting chemical formulae so we
    # want \mathrm. In some cases titles rely on no mathvariant meaning no special
    # math font.
    return r""


# printRecur would get modified accordingly.
def walk_mathml_tree_recursive(root):

    if root.tag == '{http://www.w3.org/1998/Math/MathML}mglyph':
        raise ValueError('mglphy elements cannot be converted to latex')

    if root.tag == '{http://www.w3.org/1998/Math/MathML}mtext':
        return rf'{get_latex_textstyle(root)}{{{unicode2tex(root.text)}}}'

    if root.tag == '{http://www.w3.org/1998/Math/MathML}mi':
        return rf'{get_latex_textstyle(root)}{{{unicode2tex(root.text)}}}'

    if root.tag == '{http://www.w3.org/1998/Math/MathML}mn':
        return unicode2tex(root.text)

    if root.tag == '{http://www.w3.org/1998/Math/MathML}mo':
        return unicode2tex(root.text)

    if root.tag == '{http://www.w3.org/1998/Math/MathML}msub':
        # <msub> base subscript </msub>
        assert len(root) == 2, "msub must have 2 children"
        base, subscript = root
        return rf'{{{walk_mathml_tree_recursive(base)}}}_{{{walk_mathml_tree_recursive(subscript)}}}'

    if root.tag == '{http://www.w3.org/1998/Math/MathML}msup':
        # <msup> base subscript </msup>
        assert len(root) == 2, "msup must have 2 children"
        base, superscript = root
        return rf'{{{walk_mathml_tree_recursive(base)}}}^{{{walk_mathml_tree_recursive(superscript)}}}'

    if root.tag == '{http://www.w3.org/1998/Math/MathML}msubsup':
        # <msubsup> base subscript superscript </msubsup>
        assert len(root) == 3, "msubsup must have 3 children"
        base, subscript, superscript = root
        return rf'{{{walk_mathml_tree_recursive(base)}}}_{{{walk_mathml_tree_recursive(subscript)}}}^{{{walk_mathml_tree_recursive(superscript)}}}'

    if root.tag == '{http://www.w3.org/1998/Math/MathML}mfrac':
        return rf'\frac{{{walk_mathml_tree_recursive(root[0])}}}{{{walk_mathml_tree_recursive(root[1])}}}'

    if root.tag == '{http://www.w3.org/1998/Math/MathML}mover':
        # <mover> base overscript </mover>
        base, overscript = root
        return rf'\overset{{{walk_mathml_tree_recursive(overscript)}}}{{{walk_mathml_tree_recursive(base)}}}'

    if root.tag == '{http://www.w3.org/1998/Math/MathML}munder':
        # <munder> base  underscript </munder>
        base, underscript = root
        return rf'\underset{{{walk_mathml_tree_recursive(underscript)}}}{{{walk_mathml_tree_recursive(base)}}}'

    if root.tag == '{http://www.w3.org/1998/Math/MathML}munderover':
        # <munderover> base underscript  overscript </munderover>

        base, underscript, overscript = root
        return rf'\overset{{{walk_mathml_tree_recursive(overscript)}}}{{\underset{{{walk_mathml_tree_recursive(underscript)}}}{{{walk_mathml_tree_recursive(base)}}}}}'

    if root.tag == '{http://www.w3.org/1998/Math/MathML}msqrt':
        # <msqrt> base </msqrt>
        base = ''
        for child in root:
            base += walk_mathml_tree_recursive(child)
        return rf'\sqrt{{{base}}}'

    # if root.tag == '{http://www.w3.org/1998/Math/MathML}mroot':
        # <mroot> base index </mroot>
        #  NEED TO TAKE LAST CHILD AS INDEX
        # text = ''
        # for child in root:
        #     text += walk_tree_recursive(child)
        # return rf'\sqrt[]{{{text}}}'

    text = ''
    for child in root:
        text += walk_mathml_tree_recursive(child)

    return text

def walk_html_tree_recursive(root):
    if root.tag == 'sub':
        return rf'$_{{{unicode2tex(root.text)}}}$'

    text = ''
    for child in root:
        text += walk_mathml_tree_recursive(child)

    return text


# print(walk_tree_recursive(root))

# test_string = r'Quasiparticle self-consistent GW calculation of <mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML"><mml:mrow><mml:msub><mml:mi>Sr</mml:mi><mml:mn>2</mml:mn></mml:msub><mml:msub><mml:mi>RuO</mml:mi><mml:mn>4</mml:mn></mml:msub></mml:mrow></mml:math> and <mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML"><mml:msub><mml:mi>SrRuO</mml:mi><mml:mn>3</mml:mn></mml:msub></mml:math>'

test_string = r'Theory of the Role of Covalence Fe3O4 in the Perovskite-Type Manganites<mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML" display="inline"><mml:mo>[</mml:mo><mml:mi mathvariant="normal">La</mml:mi><mml:mo>,</mml:mo><mml:mi> </mml:mi><mml:mi>M</mml:mi><mml:mo>(</mml:mo><mml:mi mathvariant="normal">II</mml:mi><mml:mo>)</mml:mo><mml:mo>]</mml:mo><mml:mi mathvariant="normal">Mn</mml:mi><mml:mrow><mml:msub><mml:mrow><mml:mi mathvariant="normal">O</mml:mi></mml:mrow><mml:mrow><mml:mn>3</mml:mn></mml:mrow></mml:msub></mml:mrow></mml:math>'

test_string=r'An Electron Diffraction Study and a Theory of the Transformation from γ-Fe<sub>2</sub>O<sub>3</sub>to α-Fe<sub>2</sub>O<sub>3</sub>, Observations of atoms consisting of π+x and π− mesons <mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML" display="inline"><mml:mo>[</mml:mo><mml:mi mathvariant="normal">La</mml:mi><mml:mo>,</mml:mo><mml:mi> </mml:mi><mml:mi>M</mml:mi><mml:mo>(</mml:mo><mml:mi mathvariant="normal">II</mml:mi><mml:mo>)</mml:mo><mml:mo>]</mml:mo><mml:mi mathvariant="normal">Mn</mml:mi><mml:mrow><mml:msub><mml:mrow><mml:mi mathvariant="normal">O</mml:mi></mml:mrow><mml:mrow><mml:mn>3</mml:mn></mml:mrow></mml:msub></mml:mrow></mml:math>'

token_functions = [
    ('mathml', re.compile(r'<(?:mml:)?math.*?>(?:(?!<\/(?:mml:)?math>).)*.*?<\/(?:mml:)?math>')),
    ('chemical', re.compile(r"(H|He|Li|Be|B|C|N|O|F|Ne|Na|Mg|Al|Si|P|S|Cl|Ar|K|Ca|Sc|Ti|V|Cr|Mn|Fe|Co|Ni|Cu|Zn|Ga|Ge|As|Se|Br|Kr|Rb|Sr|Y|Zr|Nb|Mo|Tc|Ru|Rh|Pd|Ag|Cd|In|Sn|Sb|Te|I|Xe|Cs|Ba|La|Ce|Pr|Nd|Pm|Sm|Eu|Gd|Tb|Dy|Ho|Er|Tm|Yb|Lu|Hf|Ta|W|Re|Os|Ir|Pt|Au|Hg|Tl|Pb|Bi|Po|At|Rn|Fr|Ra|Ac|Th|Pa|U|Np|Pu|Am|Cm|Bk|Cf|Es|Fm|Md|No|Lr|Rf|Db|Sg|Bh|Hs|Mt|Ds|Rg|Cn|Nh|Fl|Mc|Lv|Ts|Og)([0-9]+)")),
    ('word', re.compile(r'\w+')),
    ('whitespace', re.compile(r'\W+'))
]

def next_token(text):
    for (token_name, regex) in token_functions:
        m = regex.match(text)
        print(m)
        if m is None:
            continue
        else:
            matched_text = m.group()
            token = (token_name, matched_text)
            return token

# def tokenize(text):
#     tokens = []
#     while len(text) > 0:
#         token = next_token(text)
#         tokens.append(token)
#         print(tokens)
#         matched_text = token[1]
#         text = text[len(matched_text):]
#         print(text)
#     return tokens
#
# tokenize(test_string)

# for result in tokenize_mathml(test_string)[1]:
#     root = ET.fromstring(result)
#     print(walk_tree_recursive(root))
    # print(result)
# print(tokenize_mathml(test_string))

#https://docs.python.org/3/library/re.html#search-vs-match

from typing import NamedTuple

class Token(NamedTuple):
    type: str
    value: str
    column: int

CHEMICAL_REGEX=r"(H|He|Li|Be|B|C|N|O|F|Ne|Na|Mg|Al|Si|P|S|Cl|Ar|K|Ca|Sc|Ti|V|Cr|Mn|Fe|Co|Ni|Cu|Zn|Ga|Ge|As|Se|Br|Kr|Rb|Sr|Y|Zr|Nb|Mo|Tc|Ru|Rh|Pd|Ag|Cd|In|Sn|Sb|Te|I|Xe|Cs|Ba|La|Ce|Pr|Nd|Pm|Sm|Eu|Gd|Tb|Dy|Ho|Er|Tm|Yb|Lu|Hf|Ta|W|Re|Os|Ir|Pt|Au|Hg|Tl|Pb|Bi|Po|At|Rn|Fr|Ra|Ac|Th|Pa|U|Np|Pu|Am|Cm|Bk|Cf|Es|Fm|Md|No|Lr|Rf|Db|Sg|Bh|Hs|Mt|Ds|Rg|Cn|Nh|Fl|Mc|Lv|Ts|Og)([0-9]+)"

def tokenize(code):
    unicode_math = [re.escape(x) for x in UNICODE2TEX.keys()]
    unicode_math_regex=f"({'|'.join(unicode_math)})+"
    token_specification = [
        ('MATHML',   r'<(?:mml:)?math.*?>(?:(?!<\/(?:mml:)?math>).)*.*?<\/(?:mml:)?math>'),  # mathml
        ('HTML', r'<(sub|sup|b|i|em).*?>(?:(?!<\/(sub|sup|b|i|em)>).)*.*?<\/(sub|sup|b|i|em)>'),  # mathml
        ('UNICODEMATH', unicode_math_regex),
        ('CHEMICAL', CHEMICAL_REGEX),
        ('NOUN',   r"[A-Za-z]*[A-Z][A-Za-z]*"),  # has a capital letter somewhere within the word
        ('PUNCTUATION', r"[-.,:?]"),
        ('WORD', r"((?![<>/])[\w]+)"),  # word
        ('WHITESPACE', r"\W"),
        ('MISMATCH', r'.'),  # Any other character
    ]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    line_start = 0

    trans = str.maketrans(UNICODE2TEX)

    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start() - line_start
        if kind == 'NOUN':
            value = f'{{{value.translate(trans)}}}'
        if kind == 'WORD':
            value = value.translate(trans)
        if kind == 'WHITESPACE':
            pass
        if kind == 'UNICODEMATH':
            value = f'${value.translate(trans)}$'
        if kind == 'MATHML':
            root = ET.fromstring(value)
            value = f'${walk_mathml_tree_recursive(root)}$'
        if kind == 'HTML':
            root = ET.fromstring(value)
            value = f'{walk_html_tree_recursive(root)}'
        if kind == 'CHEMICAL':
            value = re.sub(CHEMICAL_REGEX, r'\g<1>$_{\g<2>}$', value)
        elif kind == 'MISMATCH':
            raise RuntimeError(f'{value!r} unexpected')
        yield Token(kind, value, column)

for token in tokenize(test_string):
    print(token.type, token.value)

text = ''.join([token.value for token in tokenize(test_string)])
print(text)

# for token in tokenize(test_string):
#     print(token.value)