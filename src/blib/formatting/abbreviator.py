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
            for word_pattern, abbreviation in abbreviation_dictionary.items():
                self.insert_abbreviation(word_pattern, abbreviation)


    @staticmethod
    def __stem(word, length=3):
        """Returns the stem of a word in lowercase where the stem is the first `length`
        characters of the word.
        """
        return word[0:length].lower()


    def insert_abbreviation(self, word_pattern, abbreviation):
        """Inserts a word from the abbreviation dictionary"""
        stem = self.__stem(word_pattern)

        if not (stem in self.__abbreviation_dictionary):
            self.__abbreviation_dictionary[stem] = {}
        self.__abbreviation_dictionary[stem][word_pattern] = abbreviation


    def remove_abbreviation(self, word_pattern):
        """Removes a word from the abbreviation dictionary"""
        del self.__abbreviation_dictionary[self.__stem(word_pattern)][word_pattern]


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

        for word_pattern, abbreviation in self.__abbreviation_dictionary[stem].items():
            # We must use "\b{word_pattern}\b" to make sure whole words are matched in general,
            # for example otherwise r'internal': r'intern.', would pre-emptively match
            # 'international' when it should only have matched 'internal' (i.e. a whole word).
            # International is matched later by r'internation\S*': r'int.',
            abbreviated_word, num_substitutions = re.subn(
                fr"\b{word_pattern}\b", abbreviation, word, flags=re.IGNORECASE)
            if num_substitutions != 0:
                # The abbreviation dictionary is assumed to be independent of case
                # (so that for example Journal -> J. and journal -> j. don't have
                # to both be defined). The abbreviated word is therefore in lower case
                # only. So we copy the case from the original word
                return self.__copy_case(word, abbreviated_word)

        # If no abbreviation is found then the word is returned unabbreviated. Note that
        # the case of the letters is preserved, this is important because it could be
        # an acronym so we don't want to make assumptions that it should be title cased.
        return word


    @lru_cache(maxsize=32)
    def abbreviate(self, string):
        abbreviated_parts = []

        for word in string.split():
            abbreviated_parts.append(self.__abbreviate_word(word))

        # the filter removes any empty strings, for example where we have removed entire words from
        # an abbreviation (e.g. 'of' -> '')
        return ' '.join(filter(None, abbreviated_parts))
