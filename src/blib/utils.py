import itertools

from unidecode import unidecode


def normalise_unicode_to_ascii(string):
    """
    Removes any non-ascii characters from the string, replacing them with latin equivalents if possible
    """
    return unidecode(string)


def flatten(x):
    """
    Flattens an iteratable object into a string
    """
    if isinstance(x, str):
        return x

    return ''.join(itertools.chain.from_iterable(x))
