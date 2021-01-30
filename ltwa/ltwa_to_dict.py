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

with io.open(LTWA_FILE, 'r', encoding='utf16') as f:
    for line in f.readlines():
        data = line.split()
        word_pattern = data[0]
        word_replacement = data[1]

        if word_replacement == 'n.a.':
            # this word does not get abbreviated in ISO 4
            continue
        languages = [x.replace(',','') for x in data[2:]]

        if 'eng' in languages:
            regex_word_pattern = word_pattern
            regex_word_pattern = re.sub(r'^-', r'\\S+', regex_word_pattern)
            regex_word_pattern = re.sub(r'-$', r'\\S*', regex_word_pattern)

            print(f"r'{regex_word_pattern}': r'{word_replacement}',")
print('}')