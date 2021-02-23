import re
import unicodedata


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


#TODO handle specials such as < > and degree (see https://en.wikibooks.org/wiki/LaTeX/Special_Characters)
def encode_tex_specials(string):

    # if the string is pure ascii then there is nothing to encode into tex
    if is_ascii(string):
        return string

    tex_specials = {
        # greek
        b'\u03b1': b'\u0024\u005c\u0061\u006c\u0070\u0068\u0061\u0024', # "α": "$\alpha$ U+03B1 greek small letter alpha
        # characters
        b'a\u030a': b'\u007b\u005c\u0061\u0061\u007d',  # "å": "{\aa}" U+00E5 latin small letter a with ring above
        b'\u0131': b'\u007b\u005c\u0069\u007d',         # "ı": "{\i}"  U+0131 latin small letter dotless i
        b'\u0141': b'\u007b\u005c\u004c\u007d',         # "Ł": "{\L}"  U+0142 latin capital letter l with stroke
        b'\u0142': b'\u007b\u005c\u006c\u007d',         # "ł": "{\l}"  U+0142 latin small letter l with stroke
        b'\\xa1': b'\u007b\u0021\u0060\u007d',          # "¡": "{!`}"  U+00A1 inverted exclamation mark
        b'\\xbf': b'\u007b\u003f\u0060\u007d',          # "¿": "{?`}"  U+00BF inverted question mark
        b'\\xd8': b'\u007b\u005c\u004f\u007d',          # "Ø": "{\O}"  U+00F8 latin capital letter o with stroke
        b'\\xf8': b'\u007b\u005c\u006f\u007d',          # "ø": "{\o}"  U+00F8 latin small letter o with stroke
        b'\\xdf': b'\u007b\u005c\u0073\u0073\u007d',    # "ß": "{\ss}" U+00DF latin small letter sharp s
        # punctuation
        b'\u2009': b'\u0020',                           # " ": " "  U+2009 thin space
        b'\u2010': b'\u002d',                           # "‐": "-"     U+2010 hyphen
        b'\u2011': b'\u002d',                           # "‑": "-"     U+2011 non-breaking hyphen
        b'\u2012': b'\u002d',                           # "‒": "-"     U+2012 figure dash
        b'\u2013': b'\u002d\u002d',                     # "–": "--"    U+2013 en dash
        b'\u2014': b'\u002d\u002d\u002d',               # "—": "---"   U+2013 em dash
        b'\u2018': b'\u0060',                           # "‘": "`"     U+2018 left single quotation mark
        b'\u2019': b'\u0027',                           # "’": "'"     U+2019 right single quotation mark
        b'\u201c': b'\u0060\u0060',                     # "“": "``"    U+201C left double quotation mark
        b'\u201d': b'\u0027\u0027',                     # "”": "''"    U+201D right double quotation mark
        # ligatures
        b'\ufb01': b'\u0066\u0069',                     # "ﬁ": "fi"    U+FB01 latin small ligature fi
        b'\ufb02': b'\u0066\u006c',                     # "ﬂ": "fl"    U+FB02 latin small ligature fl
        b'\ufb03': b'\u0066\u0066\u0069',               # "ﬃ": "ffi"  U+FB03 latin small ligature ffi
        b'\ufb04': b'\u0066\u0066\u006c',               # "ﬄ": "ffl"  U+FB04 latin small ligature ffl
    }
    # encode to unicode escaped byte string
    byte_string = unicodedata.normalize('NFKD', string).encode('unicode-escape')
    for unicode_char, tex_char in tex_specials.items():
        regex = re.compile(re.escape(unicode_char))
        byte_string = regex.sub(re.escape(tex_char), byte_string)
    return byte_string.decode('unicode-escape')


def encode_tex_diacritics(string):
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
    if is_ascii(string):
        return string

    tex_diacritics = {
        b'\u0300': b'\u005c\u0060',        # r'\`',  # grave accent
        b'\u0301': b'\u005c\u0027',        # r'\'',  # acute accent
        b'\u0302': b'\u005c\u005e',        # r'\^',  # circumflex accent
        b'\u0303': b'\u005c\u007e',        # r'\~',  # tilde over letter
        b'\u0304': b'\u005c\u003d',        # r'\=',  # macron
        b'\u0306': b'\u005c\u0075\u0020',  # r'\u ', # breve accent
        b'\u0307': b'\u005c\u002e',        # r'\.',  # dot accent
        b'\u0308': b'\u005c\u0022',        # r'\"',  # diaeresis (umlaut)
        b'\u030a': b'\u005c\u0072\u0020',  # r'\r '  # ring above
        b'\u030b': b'\u005c\u0048\u0020',  # r'\H ', # long Hungarian umlaut (double acute accent)
        b'\u030c': b'\u005c\u0076\u0020',  # r'\v ', # caron (hacek)
        b'\u0323': b'\u005c\u0064\u0020',  # r'\d ', # dot-under accent
        b'\u0327': b'\u005c\u0063\u0020',  # r'\c ', # cedilla
        b'\u0328': b'\u005c\u006b\u0020',  # r'\k ', # ogonek
        b'\u0331': b'\u005c\u0062\u0020',  # r'\b ', # bar-under accent
        b'\u0361': b'\u005c\u0074\u0020',  # r'\t ', # double inverted breve (tie)
    }

    # encode to unicode escaped byte string decomposition characters
    byte_string = unicodedata.normalize('NFKD', string).encode('unicode-escape')

    # loop through all diacritics and attempt a substitution in the string
    for unicode_dia, tex_dia in tex_diacritics.items():
        regex = re.compile(b'([a-zA-Z])' + re.escape(unicode_dia))
        byte_string = regex.sub(b'{' + re.escape(tex_dia) + b'\g<1>}', byte_string)

    return byte_string.decode('unicode-escape')


def encode_tex(string):
    # if the string is pure ascii then there is nothing to encode into tex
    if is_ascii(string):
        return string

    return encode_tex_diacritics(encode_tex_specials(string))
