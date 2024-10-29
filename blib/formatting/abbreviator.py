import re
from functools import lru_cache


class Abbreviator:
    """Abbreviates strings based on a regular expression map

    Words which are not matched in the abbreviation dictionary are not abbreviated.

    The abbreviation dictionary is assumed to be independent of case. So for example
    Journal -> J. and journal -> j don't both have to be defined. The final case of the abbreviation
    is copied over from the full word being abbreviated.

    Words which should be completely removed from abbreviations should map to an empty string.
    For example `abbreviator.insert('of', '')`.

    """
    __abbreviation_dictionary = {}

    def __init__(self, abbreviation_dictionary=None):
        if abbreviation_dictionary:
            for word, abbrev in abbreviation_dictionary.items():
                self.insert(word, abbrev)

    @staticmethod
    def __stem(word):
        return word[0:3].lower()


    def insert(self, word, abbrev):
        """Inserts a word from the abbreviation dictionary"""
        stem = self.__stem(word)
        if not (stem in self.__abbreviation_dictionary):
            self.__abbreviation_dictionary[stem] = {}
        self.__abbreviation_dictionary[stem][word] = abbrev


    def remove(self, word):
        """Removes a word from the abbreviation dictionary"""
        del self.__abbreviation_dictionary[self.__stem(word)][word]


    def __copy_case(self, word, abbrev):
        """
        Copies the captialisation from word onto the abbreviation
        :param word:
        :param abbrev:
        :return:
        """
        result = []
        for word_char, abbrev_char in zip(word, abbrev):
            if word_char.lower() == abbrev_char.lower():
                if word_char.isupper():
                    result.append(word_char)
                    continue
            result.append(abbrev_char)

        return ''.join(result)

    @lru_cache(maxsize=64)
    def __abbreviate_word(self, word):

        stem = self.__stem(word)

        if stem not in self.__abbreviation_dictionary:
            return word

        for pattern, abbreviation in self.__abbreviation_dictionary[stem].items():
            # We must use "\b{pattern}\b" to make sure whole words are matched in general,
            # for example otherwise r'internal': r'intern.', would pre-emptively match
            # 'international' when it should only have matched 'internal' (i.e. a whole word).
            # International is matched later by r'internation\S*': r'int.',
            abbrev_word, nsubs = re.subn(fr"\b{pattern}\b", abbreviation, word, flags=re.IGNORECASE)
            if nsubs != 0:
                # The abbreviation dictionary is assumed to be independent of case
                # (so that for example Journal -> J. and journal -> j. don't have
                # to both be defined). The abbreviated word is therefore in lower case
                # only. So we copy the case from the original word
                return self.__copy_case(word, abbrev_word)

        # If no abbreviation is found then the word is returned unabbreviated. Note that
        # the case of the letters is preserved, this is important because it could be
        # an acronym so we don't want to make assumptions that it should be title cased.
        return word


    @lru_cache(maxsize=32)
    def abbreviate(self, string):
        abbrev = []

        for word in string.split():
            abbrev.append(self.__abbreviate_word(word))

        # the filter removes any empty strings, for example where we have removed entire words from
        # an abbreviation (e.g. 'of' -> '')
        return ' '.join(filter(None, abbrev))
