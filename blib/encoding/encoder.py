import xml.etree.ElementTree as ET
from typing import NamedTuple

# We use the third party 'regex' module rather than pythons native 're' module because it has
# more advanced support for unicode. Specifically it supports the \p{} syntax
# (https://www.regular-expressions.info/unicode.html)
# which allows us to identify unicode letter and punctuation more reliably. This is important
# for example when an author name has diacritics. In unicode these may use 'combining marks'
# which depending on the formatting can come before or after the letter, for example U+0306 is
# a breve '‘̆' which will appear after a letter such as in 's̆'. Without using \p{} syntax it's
# extemely difficult to capture the breve with the letter. With the \p{} syntax we can use
# [\p{L}\p{M}] which captures letters and combining marks on letters.
import regex as re


class Encoder:

    # The regex patterns for tokenizing are available externally so that clients can use them if needed

    # Matches all text which is between mathml opening and closing tags with the optional mml namespace
    # For example:
    #   <math>...any text...</math>
    #   <mml:math>...any text...</mml:math>
    #   <mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML">...any text...</mml:math>
    _token_regex_mathml = r'<(?:mml:)?math.*?>(?:(?!<\/(?:mml:)?math>).)*.*?<\/(?:mml:)?math>'

    # Matches all text which is between html formatting tags which we can sensibly format. Currently
    # - superscripts
    # - subscripts
    # - bold
    # - italic
    # For example:
    #   <sub>...any text...</sub>
    #   <sup>...any text...</sup>
    #   <b>...any text...</b>
    #   <i>...any text...</i>
    _token_regex_html = r'<(sub|sup|b|i|tt).*?>(?:(?!<\/(sub|sup|b|i|tt)>).)*.*?<\/(sub|sup|b|i|tt)>'

    # Regex for matching unicode symbols which we consider to be 'mathematical'.
    # Greek and Coptic Block: \u0370-\u03ff
    # Mathematical Operators Block: \u2200-\u22ff
    _token_regex_unicodemath = r"([\u0370-\u03ff]|[\u2200-\u22ff])+"

    # Regex for matching chemical formula. This will detect element names followed by numbers,
    # for example Fe2O3, C60. We will often want to typeset these properly so the numbers are subscripted.
    # Formula without numbers such as NiO are not matched because they don't need any special typesetting.
    _token_regex_chemical = r"((?:H|He|Li|Be|B|C|N|O|F|Ne|Na|Mg|Al|Si|P|S|Cl|Ar|K|Ca|Sc|Ti|V|Cr|Mn|Fe|Co|Ni|Cu|Zn|Ga|Ge|As|Se|Br|Kr|Rb|Sr|Y|Zr|Nb|Mo|Tc|Ru|Rh|Pd|Ag|Cd|In|Sn|Sb|Te|I|Xe|Cs|Ba|La|Ce|Pr|Nd|Pm|Sm|Eu|Gd|Tb|Dy|Ho|Er|Tm|Yb|Lu|Hf|Ta|W|Re|Os|Ir|Pt|Au|Hg|Tl|Pb|Bi|Po|At|Rn|Fr|Ra|Ac|Th|Pa|U|Np|Pu|Am|Cm|Bk|Cf|Es|Fm|Md|No|Lr|Rf|Db|Sg|Bh|Hs|Mt|Ds|Rg|Cn|Nh|Fl|Mc|Lv|Ts|Og)+)([0-9]?[0-9mnxyzαβγδεζηθκλμνξσ]+[\-−]?[0-9]?[0-9mnxyzαβγδεζηθκλμνξσ]?)(?=$|\s|H|He|Li|Be|B|C|N|O|F|Ne|Na|Mg|Al|Si|P|S|Cl|Ar|K|Ca|Sc|Ti|V|Cr|Mn|Fe|Co|Ni|Cu|Zn|Ga|Ge|As|Se|Br|Kr|Rb|Sr|Y|Zr|Nb|Mo|Tc|Ru|Rh|Pd|Ag|Cd|In|Sn|Sb|Te|I|Xe|Cs|Ba|La|Ce|Pr|Nd|Pm|Sm|Eu|Gd|Tb|Dy|Ho|Er|Tm|Yb|Lu|Hf|Ta|W|Re|Os|Ir|Pt|Au|Hg|Tl|Pb|Bi|Po|At|Rn|Fr|Ra|Ac|Th|Pa|U|Np|Pu|Am|Cm|Bk|Cf|Es|Fm|Md|No|Lr|Rf|Db|Sg|Bh|Hs|Mt|Ds|Rg|Cn|Nh|Fl|Mc|Lv|Ts|Og)"


    # Regex for matching nouns. We define nouns as any word which contains (ASCII) capital letters. This does not
    # necessarily have to be at the start of the word. Capital letters in the middle or end of a word usually indicate
    # that the word should be treated as a noun too.
    _token_regex_noun = r"[\p{L}\p{M}\p{N}]*[\p{Lu}\p{M}][\p{L}\p{M}\p{N}]*"

    # Regex pattern for matching characters we consider as punctuation. These could be ASCII or unicode.
    _token_regex_punctuation = r"\p{P}"

    # Regex pattern for matching anything which looks like a normal standalone word.
    _token_regex_word = r"((?![<>\/])[\p{L}\p{M}\p{N}]+)"

    # Regex pattern for matching anything which looks like a normal standalone word.
    _token_regex_symbol = r"(°)+"

    # Regex pattern for matching newlines.
    _token_regex_newline = r"\n\s*"

    # Regex pattern for matching whitespace.
    _token_regex_whitespace = r"\p{Zs}"

    class Token(NamedTuple):
        type: str
        value: str
        position: int

    def _tokenize(self, text):
        """
        Tokenize `text` into a series of Token objects which store the token type, the tokenized string which belongs
        to that token and the start position within the `text` string of the tokenized string.

        This function yields and should normally be used as an iterator in a for statement. For example:

            for token in self._tokenize(text):
                # do something with the tokens
        """

        # The order of this list is important. The string will be checked against each token regex in turn, so in
        # principle the most complex matching needs to happen first and the simplest matches (which may be contained
        # within a more complex match) should happen later. For example a NOUN is a word which starts with a capital,
        # so we must have first checked for chemical formulae which will also start with a capital letter.
        token_specification = [
            ('MATHML',      self._token_regex_mathml),
            ('HTML',        self._token_regex_html),
            ('UNICODEMATH', self._token_regex_unicodemath),
            ('SYMBOL',      self._token_regex_symbol),
            ('CHEMICAL',    self._token_regex_chemical),
            ('PUNCTUATION', self._token_regex_punctuation),
            ('NOUN',        self._token_regex_noun),
            ('WORD',        self._token_regex_word),
            ('NEWLINE',     self._token_regex_newline),
            ('WHITESPACE',  self._token_regex_whitespace),
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
            yield self.Token(kind, value, position)

    def _walk_html_tree(self, root):
        if root.tag == 'sub':
            return self.encode_html_sub(root)

        if root.tag == 'sup':
            return self.encode_html_sup(root)

        if root.tag == 'b':
            return self.encode_html_b(root)

        if root.tag == 'i':
            return self.encode_html_i(root)

        if root.tag == 'tt':
            return self.encode_html_tt(root)

        text = ''
        for child in root:
            text += self._walk_html_tree(child)

        return text

    def _walk_mathml_tree(self, root):
        if root.tag == '{http://www.w3.org/1998/Math/MathML}mglyph':
            raise ValueError('mglphy elements cannot be encoded')

        if root.tag == '{http://www.w3.org/1998/Math/MathML}mtext':
            return self.encode_mathml_mtext(root)

        if root.tag == '{http://www.w3.org/1998/Math/MathML}mi':
            return self.encode_mathml_mi(root)

        if root.tag == '{http://www.w3.org/1998/Math/MathML}mn':
            return self.encode_mathml_mn(root)

        if root.tag == '{http://www.w3.org/1998/Math/MathML}mo':
            return self.encode_mathml_mo(root)

        if root.tag == '{http://www.w3.org/1998/Math/MathML}msub':
            # <msub> base subscript </msub>
            assert len(root) == 2, "msub must have 2 children"
            return self.encode_mathml_msub(root)

        if root.tag == '{http://www.w3.org/1998/Math/MathML}msup':
            # <msup> base subscript </msup>
            assert len(root) == 2, "msup must have 2 children"
            return self.encode_mathml_msup(root)

        if root.tag == '{http://www.w3.org/1998/Math/MathML}msubsup':
            # <msubsup> base subscript superscript </msubsup>
            return self.encode_mathml_msubsup(root)

        if root.tag == '{http://www.w3.org/1998/Math/MathML}mfrac':
            return self.encode_mathml_mfrac(root)

        if root.tag == '{http://www.w3.org/1998/Math/MathML}mover':
            # <mover> base overscript </mover>
            return self.encode_mathml_mover(root)

        if root.tag == '{http://www.w3.org/1998/Math/MathML}munder':
            # <munder> base  underscript </munder>
            return self.encode_mathml_munder(root)

        if root.tag == '{http://www.w3.org/1998/Math/MathML}munderover':
            # <munderover> base underscript  overscript </munderover>
            return self.encode_mathml_munderover(root)

        if root.tag == '{http://www.w3.org/1998/Math/MathML}msqrt':
            # <msqrt> base </msqrt>
            return self.encode_mathml_msqrt(root)

        text = ''
        for child in root:
            text += self._walk_mathml_tree(child) or ""

        return text


    def encode_noun(self, text):
        return text

    def encode_word(self, text):
        return text

    def encode_newline(self, text):
        return text

    def encode_whitespace(self, text):
        return text

    def encode_unicode_math(self, text):
        return text

    def encode_symbol(self, text):
        return text

    def encode_chemical(self, text):
        return text

    def encode_punctuation(self, text):
        return text

    def encode_html(self, text):
        return self._walk_html_tree(ET.fromstring(text))

    def encode_html_sub(self, node):
        return node.text

    def encode_html_sup(self, node):
        return node.text

    def encode_html_b(self, node):
        return node.text

    def encode_html_i(self, node):
        return node.text

    def encode_html_tt(self, node):
        return node.text

    def encode_mathml(self, text):
        return self._walk_mathml_tree(ET.fromstring(text))

    def encode_mathml_mtext(self, node):
        return node.text

    def encode_mathml_mi(self, node):
        return node.text

    def encode_mathml_mn(self, node):
        return node.text

    def encode_mathml_mo(self, node):
        return node.text

    def encode_mathml_msub(self, node):
        return node.text

    def encode_mathml_msup(self, node):
        return node.text

    def encode(self, text, nouns=False, newlines=False, chemicals=False):
        result = []

        prev_token = self.Token('MISMATCH', '', -1)

        for token in self._tokenize(text):

            # Often MathML appears butted up against text without a space in the correct space. Here we check
            # what the previous token was. If it's already a MISMATCH, WHITESPACE, PUNCTUATION or NEWLINE then
            # we don't want to insert an extra space. In any other cases let's put in a space.
            if token.type == 'MATHML' and (prev_token.type not in ('MISMATCH', 'WHITESPACE', 'PUNCTUATION','NEWLINE')):
                result.append(' ')

            if prev_token.type == 'MATHML' and (token.type not in ('MISMATCH', 'WHITESPACE', 'PUNCTUATION','NEWLINE')):
                result.append(' ')

            if token.type == 'NOUN':
                if nouns:
                    result.append(self.encode_noun(token.value))
                else:
                    result.append(self.encode_word(token.value))
            elif token.type == 'WORD':
                result.append(self.encode_word(token.value))
            elif token.type == 'PUNCTUATION':
                result.append(self.encode_punctuation(token.value))
            elif token.type == 'NEWLINE':
                # For some reason crossref often uses newlines around MathML in titles. We'll omit all newlines
                # by default.
                if newlines:
                    result.append(self.encode_newline(token.value))
            elif token.type == 'WHITESPACE':
                result.append(self.encode_whitespace(token.value))
            elif token.type == 'UNICODEMATH':
                result.append(self.encode_unicode_math(token.value))
            elif token.type == 'SYMBOL':
                result.append(self.encode_symbol(token.value))
            elif token.type == 'CHEMICAL':
                if chemicals:
                    result.append(self.encode_chemical(token.value))
                else:
                    result.append(self.encode_word(token.value))
            elif token.type == 'HTML':
                result.append(self.encode_html(token.value))
            elif token.type == 'MATHML':
                result.append(self.encode_mathml(token.value))

            prev_token = token

        return ''.join(result)

