import re

from typing import NamedTuple


# TODO: Need to try and separate when a - is used for oxidation state vs when it is a hyphen.
#       We may be able to use the fact that 5- is the lowest possible oxidation state and 9+
#       the highest.
# Single element names should come last so we have a chance to match longer ones first for example Sm will capture
# 'S' before 'Sm'
chemical_formula_regex = r"((?:He|Li|Be|Ne|Na|Mg|Al|Si|Cl|Ar|Ca|Sc|Ti|Cr|Mn|Fe|Co|Ni|Cu|Zn|Ga|Ge|As|Se|Br|Kr|Rb|Sr|Zr|Nb|Mo|Tc|Ru|Rh|Pd|Ag|Cd|In|Sn|Sb|Te|Xe|Cs|Ba|La|Ce|Pr|Nd|Pm|Sm|Eu|Gd|Tb|Dy|Ho|Er|Tm|Yb|Lu|Hf|Ta|Re|Os|Ir|Pt|Au|Hg|Tl|Pb|Bi|Po|At|Rn|Fr|Ra|Ac|Th|Pa|Np|Pu|Am|Cm|Bk|Cf|Es|Fm|Md|No|Lr|Rf|Db|Sg|Bh|Hs|Mt|Ds|Rg|Cn|Nh|Fl|Mc|Lv|Ts|Og|H|B|C|K|N|O|F|P|S|Y|I|W|U|V)+)([0-9]?[0-9mnxyzαβγδεζηθκλμνξσ]+[\-−]?[0-9]?[0-9mnxyzαβγδεζηθκλμνξσ]?)(?=$|\s|He|Li|Be|Ne|Na|Mg|Al|Si|Cl|Ar|Ca|Sc|Ti|Cr|Mn|Fe|Co|Ni|Cu|Zn|Ga|Ge|As|Se|Br|Kr|Rb|Sr|Zr|Nb|Mo|Tc|Ru|Rh|Pd|Ag|Cd|In|Sn|Sb|Te|Xe|Cs|Ba|La|Ce|Pr|Nd|Pm|Sm|Eu|Gd|Tb|Dy|Ho|Er|Tm|Yb|Lu|Hf|Ta|Re|Os|Ir|Pt|Au|Hg|Tl|Pb|Bi|Po|At|Rn|Fr|Ra|Ac|Th|Pa|Np|Pu|Am|Cm|Bk|Cf|Es|Fm|Md|No|Lr|Rf|Db|Sg|Bh|Hs|Mt|Ds|Rg|Cn|Nh|Fl|Mc|Lv|Ts|Og|H|B|C|K|N|O|F|P|S|Y|I|W|U|V)"

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

