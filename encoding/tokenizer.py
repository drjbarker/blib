import re

from typing import NamedTuple

chemical_formula_regex = r"(H|He|Li|Be|B|C|N|O|F|Ne|Na|Mg|Al|Si|P|S|Cl|Ar|K|Ca|Sc|Ti|V|Cr|Mn|Fe|Co|Ni|Cu|Zn|Ga|Ge|As|Se|Br|Kr|Rb|Sr|Y|Zr|Nb|Mo|Tc|Ru|Rh|Pd|Ag|Cd|In|Sn|Sb|Te|I|Xe|Cs|Ba|La|Ce|Pr|Nd|Pm|Sm|Eu|Gd|Tb|Dy|Ho|Er|Tm|Yb|Lu|Hf|Ta|W|Re|Os|Ir|Pt|Au|Hg|Tl|Pb|Bi|Po|At|Rn|Fr|Ra|Ac|Th|Pa|U|Np|Pu|Am|Cm|Bk|Cf|Es|Fm|Md|No|Lr|Rf|Db|Sg|Bh|Hs|Mt|Ds|Rg|Cn|Nh|Fl|Mc|Lv|Ts|Og)([0-9]+)"

# Make a regex string which finds any unicode math symbols
# TODO: This should not be based on the UnicodeToLatex dict but should come directly
#       from a list of common unicode math symbols

unicode_math_regex = f"(α|γ|π)+"


class Token(NamedTuple):
    type: str
    value: str
    position: int


def tokenize(text):
    token_specification = [
        ('MATHML',   r'<(?:mml:)?math.*?>(?:(?!<\/(?:mml:)?math>).)*.*?<\/(?:mml:)?math>'),  # mathml
        ('HTML', r'<(sub|sup|b|i|em).*?>(?:(?!<\/(sub|sup|b|i|em)>).)*.*?<\/(sub|sup|b|i|em)>'),  # mathml
        ('UNICODEMATH', unicode_math_regex),
        ('CHEMICAL', chemical_formula_regex),
        ('NOUN',   r"[A-Za-z]*[A-Z][A-Za-z]*"),  # has a capital letter somewhere within the word
        ('PUNCTUATION', r"[-.,:?]"),
        ('WORD', r"((?![<>/])[\w]+)"),  # word
        ('WHITESPACE', r"\W"),
        ('MISMATCH', r'.'),  # Any other character
    ]
    token_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    line_start = 0

    for x in re.finditer(token_regex, text):
        kind = x.lastgroup
        value = x.group()
        position = x.start() - line_start
        if kind == 'MISMATCH':
            raise RuntimeError(f'{value!r} unexpected')
        yield Token(kind, value, position)

