import itertools
import unicodedata

import regex as re
from unidecode import unidecode


_SPACING_ACCENT_TO_COMBINING = {
    "`": "\u0300",
    "´": "\u0301",
    "^": "\u0302",
    "~": "\u0303",
    "¯": "\u0304",
    "˘": "\u0306",
    "˙": "\u0307",
    "¨": "\u0308",
    "˚": "\u030A",
    "˝": "\u030B",
    "ˇ": "\u030C",
    "¸": "\u0327",
    "˛": "\u0328",
}

_SPACING_ACCENT_PATTERN = re.compile(
    f"([{re.escape(''.join(_SPACING_ACCENT_TO_COMBINING))}])(\\p{{L}})"
)


def normalise_unicode_to_ascii(string):
    """
    Removes any non-ascii characters from the string, replacing them with latin equivalents if possible
    """
    return unidecode(string)


def normalise_spacing_accents(string):
    """
    Convert TeX-style spacing accents before letters, e.g. "Moir´e", into composed unicode.
    """
    text = _SPACING_ACCENT_PATTERN.sub(
        lambda match: match.group(2) + _SPACING_ACCENT_TO_COMBINING[match.group(1)],
        string,
    )
    return unicodedata.normalize("NFC", text)


def flatten(x):
    """
    Flattens an iteratable object into a string
    """
    if isinstance(x, str):
        return x

    return ''.join(itertools.chain.from_iterable(x))
