import re

from .encoder import Encoder


class UnicodeEncoder(Encoder):

    def encode_subscript_digits(self, digit):
        """
        Encodes a digit 0-9 into a unicode subscript ₀-₉

        :param digit: single digit (0-9) as int or string
        :return: unicode string of subscript form of digit
        """
        digit_int = int(digit)
        assert digit_int >= 0 and digit_int <= 9
        return f'{chr(0x2080 + digit_int)}'


    def encode_chemical(self, text):
        match = re.match(self._chemical_formula_regex, text)
        # append the element name
        result = [match.group(1)]
        # now append any subscript numbers
        for num in match.group(2):
            result.append(self.encode_subscript_digits(num))

        return ''.join(result)

    def encode_html_sub(self, node):
        # If subscripts are all numeric then return the unicode subscripts
        # otherwise just return the text without making any subscript.
        if re.match(r'^[0-9]*$', node.text):
            result = []
            for num in node.text:
                result.append(self.encode_subscript_digits(num))
            return ''.join(result)
        return node.text

    def encode_mathml_mtext(self, node):
        if self._get_mathml_latex_textstyle(node):
            return rf'{self._get_mathml_latex_textstyle(node)}{{{node.text}}}'
        return node.text

    def encode_mathml_mi(self, node):
        if not node.text:
            return r"\ "
        return node.text

    def encode_mathml_mn(self, node):
        return node.text

    def encode_mathml_mo(self, node):
        return node.text

    def encode_mathml_msub(self, node):
        # <msub> base subscript </msub>
        base, subscript = node

        base_text = self._walk_mathml_tree(base)
        sub_text = self._walk_mathml_tree(subscript)

        if re.match(r'^[0-9]*$', sub_text):
            result = []
            for num in sub_text:
                result.append(self.encode_subscript_digits(num))
            sub_text = ''.join(result)

        return rf'{base_text}{sub_text}'

    def encode_mathml_msup(self, node):
        # <msub> base subscript </msub>
        base, subscript = node
        return rf'{{{self._walk_mathml_tree(base)}}}^{{{self._walk_mathml_tree(subscript)}}}'

