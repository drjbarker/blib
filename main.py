#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#TODO: fix date and 'Of' abbrev for /10.1088/0305-4608/15/6/018

import re
import requests
import argparse
import unicodedata
import json
import abbrev

from ltwa import LTWA_ABBREV

BLIB_HTTP_USER_AGENT = 'doi2bib/0.1 (mailto:j.barker@leeds.ac.uk)'

abbreviator = abbrev.Abbreviator(LTWA_ABBREV)
# appears to be an error in the LTWA that report -> rep. with no consideration of reports
abbreviator.remove(r'report')
abbreviator.insert(r'reports?', r'rep.')

abbreviator.ignore('Science')
abbreviator.ignore('Nature')

JOURNAL_ABBREV_EXTREME = {
    r'Phys\S+': 'P',
    r'Rev\S+': 'R',
    r'Lett\S+': 'L',
}

def isAscii(string):
    """
    Returns true if the string only contains ASCII characters,
    False otherwise.
    """
    try:
        string.encode('ascii')
    except UnicodeDecodeError:
        return False
    return True



def encode_tex_specials(string):
    tex_specials = {
        b'\u2009': b'\u0020',  # thin space -> space
        b'\u2010': b'\u002d',  # hyphen -> -
        b'\u2011': b'\u002d',  # non-breaking hyphen -> - (if amsmath package is used then \nobreakdash could be used)
        b'\u2012': b'\u002d',  # figure dash -> -
        b'\u2013': b'\u002d\u002d',  # en dash -> --
        b'\u2014': b'\u002d\u002d\u002d',  # em dash -> ---
        b'\u2018': b'\u0060',  # left single quotation mark
        b'\u2019': b'\u0027',  # right single quotation mark
        b'\u201c': b'\u0060\u0060',  # left double quotation mark
        b'\u201d': b'\u0027\u0027',  # right double quotation mark
        b'\\xf8': b'\u005c\u006f\u007b\u007d',  # slashed o
        b'\u0142': b'\u005c\u006c\u007b\u007d',  # slashed l
        b'\u0131': b'\u007b\u005c\u0069\u007d',  # dotless i
        # DO WE NEED LIGATURE SUPPORT HERE OR WILL NFKD ACCOUNT FOR THIS?
        # b'\ufb01': b'\u0066\u0069',  # fi ligature
        # b'\ufb02': b'\u0066\u006c',  # fl ligature
        # b'\ufb03': b'\u0066\u0066\u0069',  # ffi ligature
        # b'\ufb04': b'\u0066\u0066\u006c',  # ffl ligature
    }
    # encode to unicode escaped byte string
    bytestring = unicodedata.normalize('NFKD', string).encode('unicode-escape')
    for unicode_char, tex_char in tex_specials.items():
        regex = re.compile(re.escape(unicode_char))
        bytestring = regex.sub(re.escape(tex_char), bytestring)
    return bytestring.decode('unicode-escape')


def encode_tex_diacritics(string):
    tex_diacritics = {
        b'\u0300': b'\u005c\u0060',  # r'\`', # grave accent
        b'\u0301': b'\u005c\u0027',  # r'\'', # acute accent
        b'\u0302': b'\u005c\u005e',  # r'\^', # circumflex accent
        b'\u0303': b'\u005c\u007e',  # r'\~', # tilde over letter
        b'\u0304': b'\u005c\u003d',  # r'\=', # macron
        b'\u0306': b'\u005c\u0075',  # r'\u', # breve accent
        b'\u0307': b'\u005c\u002e',  # r'\.', # dot accent
        b'\u0308': b'\u005c\u0022',  # r'\"', # diaeresis (umlaut)
        b'\u030b': b'\u005c\u0048',  # r'\H', # long Hungarian umlaut NOT SURE IF THIS ONE IS CORRECT UNICODE
        b'\u030c': b'\u005c\u0076',  # r'\v', # caron (hacek)
        b'\u0323': b'\u005c\u0064',  # r'\d', # dot-under accent
        b'\u0327': b'\u005c\u0063',  # r'\c', # cedilla
        b'\u0328': b'\u005c\u006b',  # r'\k', # ogonek
        b'\u0331': b'\u005c\u0062',  # r'\b', # bar-under accent

    }
    # encode to unicode escaped byte string
    bytestring = unicodedata.normalize('NFKD', string).encode('unicode-escape')

    # loop through all diacritics and sub
    for unicode_dia, tex_dia in tex_diacritics.items():
        regex = re.compile(b'([a-zA-Z])' + re.escape(unicode_dia))
        bytestring = regex.sub(re.escape(tex_dia) + b'{\g<1>}', bytestring)
    return bytestring.decode('unicode-escape')


def encode_tex(string):
    encoded_string = encode_tex_specials(encode_tex_diacritics(string))
    if not isAscii(encoded_string):
        raise RuntimeWarning(f"string '{encoded_string}' contains non ASCII characters after encoding UTF8 to tex")
    return encoded_string


def doiRegex(string):
    """
    Returns the first DOI in a string. If no DOI is found it raises a ValueError.
    """
    DOI_REGEX = r'(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?![!@#%^{}",? ])\S)+)'
    match = re.search(DOI_REGEX, string)
    if not match:
        return None
    return match.group()

def arxivRegex(string):
    """
    Returns the first arXiv id in a string. If no DOI is found it raises a ValueError.

    See: https://arxiv.org/help/arxiv_identifier
    """
    ARXIV_REGEX = r'arxiv.*([0-9]{2}[0-1][0-9]\.[0-9]{4,}(?:v[0-9]+)?)'
    match = re.search(ARXIV_REGEX, string)
    if not match:
        return None
    return match.group()

def doiHttpRequest(doi, headers):
    r = requests.get(f'https://dx.doi.org/{doi}', headers=headers)
    if (r.status_code != 200):
        r.raise_for_status()
    return r

def requestBibtexFromDoi(doi):
    """
    Requests the bibtex entry for a DOI from doi.org. If found it returns as a unicode string.
    If the doi is not found it raises the returned HTTP status error from the response library.
    """
    r = doiHttpRequest(doi, {'Accept': 'text/bibliography; style=bibtex',
                             'User-Agent': BLIB_HTTP_USER_AGENT})
    r.raise_for_status()
    return r.content.decode('utf-8')


def requestJsonFromDoi(doi):
    """
    Requests the json for a DOI from doi.org.
    If the doi is not found it raises the returned HTTP status error from the response library.
    """
    r = doiHttpRequest(doi, {'Accept': 'application/citeproc+json',
                             'User-Agent': BLIB_HTTP_USER_AGENT})

    r.raise_for_status()
    return r.content


def indentBibtex(string):
    """
    Takes a oneline bibtex string and adds newlines and indents after each item
    """
    result = re.sub(r'}}$', '}\n}\n', string.strip())
    result = re.sub(r', (?=[a-zA-Z]+={.*?})', r',\n  ', result)
    return result


def bibtexItem(key, value):
    return f'{key}={{{encode_tex(value)}}}'


def cleanUnicodeToAscii(string):
    """
    Removes any non-ascii characters from the string, replacing them with latin equivalents if possible
    """
    return unicodedata.normalize('NFKD', string).encode('ascii', 'ignore').decode()


def abbreviateString(string, abbrev_mapping=LTWA_ABBREV):
    abbrev_string = string
    for word_pattern, word_replacement in abbrev_mapping.items():
        abbrev_string = re.sub(word_pattern, word_replacement, abbrev_string, flags=re.IGNORECASE)
    return abbrev_string

def removeWords(string, wordlist):
    return ' '.join([word for word in string.split() if word.lower() not in wordlist])

def hyphenToUnderscore(string):
    return re.sub(r'-', r'_', string)

def whitespaceToUnderscore(string):
    return re.sub(r'\s', r'_', string)

def endashToHyphen(string):
    return re.sub(r'\b--\b', r'-', string)

def escapeBibtexCaps(string):
    return re.sub(r'\b([A-Z])', r'{\g<1>}', string)

def processAuthorList(author_list):
    """
    Returns a bibtex formatted author list form a dictionary of given and family names
    """
    return ' and '.join(
        [f'{endashToHyphen(encode_tex(author["family"]))}, {endashToHyphen(encode_tex(author["given"]))}' for author in author_list])

def processBibtexRange(string):
    return re.sub(r'\b-\b', r'--', string)

def dictFromJson(string):
    data = json.loads(string)
    bibdict = {}

    bibdict['author'] = processAuthorList(data['author'])
    bibdict['title'] = escapeBibtexCaps(data['title'])
    bibdict['journal'] = abbreviator.abbreviate(
        removeWords(data['container-title'], {'of', 'the', 'and'}))
    bibdict['volume'] = data['volume']

    if 'issue' in data:
        bibdict['issue'] = processBibtexRange(str(data['issue']))

    if 'page' in data:
        bibdict['pages'] = processBibtexRange(data['page'])
    elif 'article-number' in data:
        bibdict['pages'] = data['article-number']

    # TODO write code for cases when an old paper is now available online so the online date is much more recent than
    # the print date (e.g. https://dx.doi.org/10.1088/0305-4608/14/7/007). Need to check for a few edge cases in all this.

    # published_print_date = []
    # published_online_date = []
    #
    # if 'published-print' in data:
    #     published_online_date = data["published-print"]['date-parts'][0]
    #
    # if 'published-online' in data:
    #     published_online_date = data["published-online"]['date-parts'][0]
    #
    if 'published-online' in data:
        bibdict['year'] = str(data["published-online"]['date-parts'][0][0])
        bibdict['month'] = str(data["published-online"]['date-parts'][0][1])
    elif 'published-print' in data:
        bibdict['year'] = str(data["published-print"]['date-parts'][0][0])
        bibdict['month'] = str(data["published-print"]['date-parts'][0][1])

    if 'publisher' in data:
        bibdict['publisher'] = data['publisher']

    bibdict['doi'] = data['DOI']
    bibdict['url'] = f'https://dx.doi.org/{data["DOI"]}'

    clean_author = cleanUnicodeToAscii(data['author'][0]['family'])
    clean_abbrev = bibdict['journal'].replace(' ','').replace('.', '').replace(':', '')
    if 'issue' in bibdict:
        clean_vol = f'{bibdict["volume"]}_{bibdict["issue"]}'
    else:
        clean_vol = f'{bibdict["volume"]}'

    identifier = whitespaceToUnderscore(hyphenToUnderscore(f"{clean_author}_{bibdict['year']}_{clean_abbrev}_{clean_vol}"))

    return identifier, bibdict


def bibtexFromJson(string):
    indetifier, bibdict = dictFromJson(string)
    bibstring = ',\n'.join([f'  {bibtexItem(k, v)}' for k, v in bibdict.items()])
    return f"@article{{{indetifier},\n{bibstring}\n}}\n"

def bibtexFromDoiString(string, method='citeproc'):
    doi = doiRegex(string)

    # It's possible we have a URL with some junk on the end which cannot be distinguished from a DOI
    # Example: https://iopscience.iop.org/article/10.1088/0953-8984/28/47/476007/meta where the DOI is
    #          10.1088/0953-8984/28/47/476007 but the doi suffix is allowed to contain non-numeric characters
    #          so we can't guarantee that the "meta" is not part of the DOI. The doiRegex function will give
    #          us "10.1088/0953-8984/28/47/476007/meta".
    # The solution below is to chomp backwards on "/" looking for a match until we have only the suffix and one prefix.
    # This might be slow if there is a lot of junk on the end because we do a http request every time

    if doi is None:
        raise ValueError('no DOI in string')

    split_doi = doi.split("/")

    for n in range(len(split_doi), 1, -1):
        trial_doi = "/".join(split_doi[0:n])
        try:
            if method == 'citeproc':
                return bibtexFromJson(requestJsonFromDoi(trial_doi))
            elif method == 'bibtex':
                return encode_tex(indentBibtex(requestBibtexFromDoi(trial_doi)))
            raise ValueError(f'invalid method: {method}')
        except requests.exceptions.HTTPError:
            # likely a 404 error because the DOI does not exist
            continue

    raise ValueError("unable to resolve DOI")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='fetch bibtex entries from a list of strings containing DOIs. '
    )

    parser.add_argument('doi', nargs='*', help='a string containing a doi')

    parser.add_argument('--file', help='a file containing dois')
    parser.add_argument('--method', choices=['citeproc', 'bibtex'], default='citeproc',
                        help='method to retrieve data from crossref')
    parser.add_argument('--comments', action='store_true', help='print search strings as bibtex comments')

    args = parser.parse_args()

    if args.doi is not None:
        for doi_string in args.doi:
            try:
                if args.comments:
                    print(f'// {doi_string.strip()}')
                print(bibtexFromDoiString(doi_string, args.method))
            except Exception as e:
                print(f'// WARNING: unable to get bibtex entry for "{doi_string}"\n')
                print(f'// {e}')
                pass

    if args.file is not None:
        processed_dois = {}
        with open(args.file) as f:
            for line in f:
                if args.comments:
                    print(f'// {line.strip()}')
                try:
                    doi = doiRegex(line)
                    if (doi is not None) and not (doi in processed_dois):
                        print(bibtexFromDoiString(line, args.method))
                        processed_dois[doi] = ''
                except Exception as e:
                    print(f'// WARNING: unable to get bibtex entry for "{line}"\n')
                    print(f'// {e}')
                    pass
