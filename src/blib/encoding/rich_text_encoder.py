import unicodedata

from .encoder import Encoder


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

class RichTextEncoder(Encoder):

    def _rtf_unicode_escape(self, string):
        string_data = []
        for character in string[:]:
            if is_ascii(character):
                string_data.append(character)
            else:
                # Rich text format requires unicode to be escaped as \uN? where N is the utf ordinal
                # and x is the replacement character to use if the unicode character has no ANSI
                # representation.
                # We can lookup the characters ordinal simply using ord(). To find ascii replacement
                # characters we can use unicodedata's normalize function. This would for example split
                # 'á' into 'a' and the accute character '◌́'. We then encode to ascii with errors='ignore'
                # which will give us only an 'a' which we can then use as the replacement character.
                # Many unicode characters cannot be decomposed and so this would result in an empty string
                # we check for this and use '?' as the replacement character in these cases.
                # There is also the possiblity that the unicode character is one of the unicode spaces (e.g.
                # non-breaking space). The nearest ascii is an ascii space, but this will then be ignored as the
                # replacement character and the following character will be used. For example "my test" will convert
                # to "\u160 test" which will then be rendered in rtf as "my est". So we also use "?" as the
                # replacement for space like characters.

                nearest_ascii = unicodedata.normalize('NFKD', character).encode('ascii', 'ignore').decode()
                if not nearest_ascii or nearest_ascii == " ":
                    nearest_ascii = '?'
                string_data.append(rf"\u{ord(character)}{nearest_ascii}")
        return ''.join(string_data)

    def _encode_text(self, text):
        return self._rtf_unicode_escape((text))

    def encode_word(self, text):
        return self._encode_text(text)

    def encode_noun(self, text):
        return self._encode_text(text)

    def encode_punctuation(self, text):
        return self._encode_text(text)

    # Our regex for punctuation is quite limited in the grand scheme of unicode so some
    # characters get classified as whitespace (non-words). Therefore we should properly
    # encode them incase they contain unicode.
    def encode_whitespace(self, text):
        return self._encode_text(text)

    def encode_unicode_math(self, text):
        return self._encode_text(text)

    def encode_html_sub(self, node):
        return rf'{{{{\sub {node.text}}}}}'

    def encode_html_b(self, node):
        return rf'\b {node.text}\b0'

    def encode_html_i(self, node):
        return rf'\i {node.text}\i0'

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
        base, subscript = node

        base_text = self._walk_mathml_tree(base)
        sub_text = self._walk_mathml_tree(subscript)

        return rf'{base_text}{{{{\sub {sub_text}}}}}'

    def encode_mathml_msup(self, node):
        base, supscript = node

        base_text = self._walk_mathml_tree(base)
        sup_text = self._walk_mathml_tree(supscript)

        return rf'{base_text}{{{{\super {sup_text}}}}}'

