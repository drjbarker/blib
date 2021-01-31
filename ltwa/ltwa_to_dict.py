#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io
import re

LTWA_FILE = "LTWA_20160915.txt"

# print('LTWA_ABBREV = {')
# with io.open(LTWA_FILE, 'r', encoding='utf16') as f:
#     for line in f.readlines():
#         data = line.split()
#         word_pattern = data[0]
#         word_replacement = data[1]
#
#         if word_replacement == 'n.a.':
#             # this word does not get abbreviated in ISO 4
#             continue
#         languages = [x.replace(',','') for x in data[2:]]
#
#         if 'eng' in languages:
#             regex_word_pattern = word_pattern
#             regex_word_pattern = re.sub(r'^-', r'\\S+', regex_word_pattern)
#             regex_word_pattern = re.sub(r'-$', r'\\S*', regex_word_pattern)
#
#             print(f"r'{regex_word_pattern}': r'{word_replacement}',")
# print('}')

print('LTWA_ABBREV = {')

# format on each line is
# fullword or stem | abbrev (or n.a.) | languages (comma separated)
# There are some times where the fullword is more than a single word
# e.g. 'Ann Arbor' or sometimes the abbrev contains spaces, e.g. U. K.
#
# The file is formatted as a tab separated format and so we can split on
# tabs to separate the fields and maintain spaces within words
#
with io.open(LTWA_FILE, 'r', encoding='utf16') as f:
    for line in f.readlines():
        data = line.strip().split('\t')
        # print(data)
        word_pattern = data[0]
        word_replacement = data[1]

        if word_replacement == 'n.a.':
            # this word does not get abbreviated in ISO 4
            continue

        # no language was defined on the line for some reason
        if not len(data) == 3:
            continue

        languages = [x.strip() for x in data[2].split(',')]

        if 'eng' in languages or 'mul' in languages:
            regex_word_pattern = word_pattern
            regex_word_pattern = re.sub(r'^-', r'\\S+', regex_word_pattern)
            regex_word_pattern = re.sub(r'-$', r'\\S*', regex_word_pattern)

            print(f"r'{regex_word_pattern}': r'{word_replacement}',")
print('}')