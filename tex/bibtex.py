import json
import re
import unicodedata
import abbrev

from tex.encoding import encode_tex

from ltwa import LTWA_ABBREV
abbreviator = abbrev.Abbreviator(LTWA_ABBREV)
# appears to be an error in the LTWA that report -> rep. with no consideration of reports
abbreviator.remove(r'report')
abbreviator.insert(r'reports?', r'rep.')

abbreviator.ignore('Science')
abbreviator.ignore('Nature')

def indentBibtex(string):
    """
    Takes a oneline bibtex string and adds newlines and indents after each item
    """
    result = re.sub(r'}}$', '}\n}\n', string.strip())
    result = re.sub(r', (?=[a-zA-Z]+={.*?})', r',\n  ', result)
    return result


def normalise_unicode_to_ascii(string):
    """
    Removes any non-ascii characters from the string, replacing them with latin equivalents if possible
    """
    return unicodedata.normalize('NFKD', string).encode('ascii', 'ignore').decode()


# def abbreviateString(string, abbrev_mapping=LTWA_ABBREV):
#     abbrev_string = string
#     for word_pattern, word_replacement in abbrev_mapping.items():
#         abbrev_string = re.sub(word_pattern, word_replacement, abbrev_string, flags=re.IGNORECASE)
#     return abbrev_string

def removeWords(string, wordlist):
    return ' '.join([word for word in string.split() if word.lower() not in wordlist])

def hyphenToUnderscore(string):
    return re.sub(r'-', r'_', string)

def whitespaceToUnderscore(string):
    return re.sub(r'\s', r'_', string)

def underscoreify(string):
    return re.sub(r'\W+', r'_', string)

def endashToHyphen(string):
    return re.sub(r'\b--\b', r'-', string)

def escapeBibtexCaps(string):
    # Rather than using (for example) "{T}est" we should do "{Test}"
    # to avoid messing with font kerning (see https://tex.stackexchange.com/a/140071)

    return re.sub(r'(\S*[A-Z]\S*)', r'{\g<1>}', string)


def remove_breaking_characters(string):
    return re.sub(r'[\n\t]', r'', string)

def processBibtexRange(string):
    return re.sub(r'\b-\b', r'--', string)


def cite_key(parts):
    return underscoreify("_".join(parts))


def extract_canonical_published_date(data):
    # For some old papers from some publishers both the original print published date and the online published date are
    # defined. The online published date is set to the date when the pdf because available online which can be very
    # different from the original publication date (e.g. 10.1088/0305-4608/14/7/007 where the print date is 1984 but
    # the online date is 2000). So we need to check which values are defined and if both are set then we need to take
    # the earlier of the two dates because with modern publishing it is common to publish online before the print
    # edition is published.
    published_print_date = {}
    published_online_date = {}

    # TODO Deal with cases where there is only a year specified e.g. 10.1128/jb.165.3.929-936.1986
    if 'published-print' in data:
        published_print_date['year'] = str(data["published-print"]['date-parts'][0][0])
        published_print_date['month'] = str(data["published-print"]['date-parts'][0][1])

    if 'published-online' in data:
        published_online_date['year'] = str(data["published-online"]['date-parts'][0][0])
        published_online_date['month'] = str(data["published-online"]['date-parts'][0][1])

    if published_print_date and published_online_date:
        if int(published_print_date['year']) < int(published_online_date['year']):
            year = published_print_date['year']
            month = published_print_date['month']
        else:
            year = published_online_date['year']
            month = published_online_date['month']
    elif published_print_date:
        year = published_print_date['year']
        month = published_print_date['month']
    elif published_online_date:
        year = published_online_date['year']
        month = published_online_date['month']
    else:
        raise RuntimeError("failed to extract date")

    return year, month


def extract_pages(data):
    if 'page' in data:
        return processBibtexRange(data['page'])
    elif 'article-number' in data:
        return data['article-number']

    raise RuntimeError("failed to extract pages")


def extract_issue(data):
    if 'issue' in data:
        return processBibtexRange(str(data['issue']))
    return None


def extract_author(data):
    return ' and '.join(
        [f'{endashToHyphen(encode_tex(author["family"]))}, {endashToHyphen(encode_tex(author["given"]))}' for author
         in data['author']])


def complex_substitution(string):
    regex = re.compile(r'(ab)\s*(initio)', flags=re.IGNORECASE)
    return regex.sub(r' \g<1> \g<2> ', string)

def extract_title(data):
    cleaned_title = escapeBibtexCaps(encode_tex(remove_breaking_characters(
        complex_substitution(data['title']))))
    return cleaned_title.strip()


def extract_journal(data, abbreviate=True):
    if abbreviate:
        return abbreviator.abbreviate(removeWords(data['container-title'], {'of', 'the', 'and'}))
    return data['container-title']


def bibtex_item(key, value):
    return f'{key}={{{encode_tex(value)}}}'


def generate_bibtex_entry(string):
    cite_key, data = dictFromJson(string)
    fields = ',\n'.join([f'  {bibtex_item(k, v)}' for k, v in data['fields'].items()])
    return (
        f"@{data['entry']}{{{cite_key},\n"
        f"{fields}\n"
        f"}}\n"
    )


def dictFromJson(string):
    data = json.loads(string)

    if data['type'] != 'article-journal':
        raise RuntimeError('DOI is not a journal article type')

    bibdict = {
        'entry': 'article',
        'fields': {}
    }

    bibdict['fields']['author'] = extract_author(data)
    bibdict['fields']['title'] = extract_title(data)
    bibdict['fields']['journal'] = extract_journal(data)
    bibdict['fields']['volume'] = data['volume']
    bibdict['fields']['issue'] = extract_issue(data)
    bibdict['fields']['pages'] = extract_pages(data)
    bibdict['fields']['year'], bibdict['fields']['month'] = extract_canonical_published_date(data)

    if 'publisher' in data:
        bibdict['fields']['publisher'] = data['publisher']

    bibdict['fields']['doi'] = data['DOI']
    bibdict['fields']['url'] = f'https://dx.doi.org/{data["DOI"]}'

    cite_key_author = normalise_unicode_to_ascii(data['author'][0]['family'])
    cite_key_journal = bibdict['fields']['journal'].replace(' ', '').replace('.', '').replace(':', '')

    if 'issue' in bibdict['fields']:
        cite_key_vol = f"{bibdict['fields']['volume']}_{bibdict['fields']['issue']}"
    else:
        cite_key_vol = f"{bibdict['fields']['volume']}"

    key = cite_key([cite_key_author, bibdict['fields']['year'], cite_key_journal, cite_key_vol])

    return key, bibdict