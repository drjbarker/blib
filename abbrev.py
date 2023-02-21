import re
from functools import lru_cache


class Abbreviator:
    __abbrev_word_map = {}
    __ignored_map = {}

    def __init__(self, abbrev_word_map, ignored_map={}):
        for word, abbrev in abbrev_word_map.items():
            self.insert(word, abbrev)
        self.__ignored_map = ignored_map

    @staticmethod
    def __stem(word):
        return word[0:3].lower()

    def insert(self, word, abbrev):
        stem = self.__stem(word)
        if not (stem in self.__abbrev_word_map):
            self.__abbrev_word_map[stem] = {}
        self.__abbrev_word_map[stem][word] = abbrev

    def remove(self, word):
        del self.__abbrev_word_map[self.__stem(word)][word]

    def ignore(self, string):
        self.__ignored_map[string] = ''


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
        if len(word) == 1:
            return word

        stem =  self.__stem(word)
        if stem not in self.__abbrev_word_map:
            return word

        for pattern, replacement in self.__abbrev_word_map[stem].items():
            # We must use "\b{pattern}\b" to make sure whole words are matched in general,
            # for example otherwise r'internal': r'intern.', would premptively match
            # 'international' when it should only have matched 'internal' (i.e. a whole word).
            # International is matched later by r'internation\S*': r'int.',
            abbrev_word, nsubs = re.subn(fr"\b{pattern}\b", replacement, word, flags=re.IGNORECASE)
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

        # if the whole string (after stripping whitespace) matches a whole string in the ignored map then
        # do not abbreviate. This IS a case sensitive match.
        if string.strip() in self.__ignored_map:
            return string

        for word in string.split():
            abbrev.append(self.__abbreviate_word(word))

        # the filter removes any empty strings, for example where we have removed entire words from an abbrevation
        # ('Of' is a common example)
        return ' '.join(filter(None, abbrev))
