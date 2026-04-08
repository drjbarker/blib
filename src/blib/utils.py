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
_MOJIBAKE_MARKERS = ("Ã", "Â", "â")


def normalise_unicode_to_ascii(string):
    """
    Removes any non-ascii characters from the string, replacing them with latin equivalents if possible
    """
    return unidecode(string)


def normalise_mojibake_utf8(string):
    """
    Repair common mojibake caused by UTF-8 text being decoded as latin-1 or cp1252.
    """
    if not any("\u0080" <= character <= "\u009f" for character in string) and not any(
        marker in string for marker in _MOJIBAKE_MARKERS
    ):
        return string

    candidates = [string]

    for encoding in ("latin-1", "cp1252"):
        try:
            candidates.append(string.encode(encoding).decode("utf-8"))
        except UnicodeError:
            continue

    def score(text):
        return (
            sum("\u0080" <= character <= "\u009f" for character in text),
            sum(text.count(marker) for marker in _MOJIBAKE_MARKERS),
        )

    return min(candidates, key=score)


def normalise_spacing_accents(string):
    """
    Repair common mojibake and convert TeX-style spacing accents before letters into composed unicode.
    """
    string = normalise_mojibake_utf8(string)
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
