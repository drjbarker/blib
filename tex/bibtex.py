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


def indent_bibtex(string):
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

def latex_chemical_formula(string):
    chemical_formula_regex = r"(H|He|Li|Be|B|C|N|O|F|Ne|Na|Mg|Al|Si|P|S|Cl|Ar|K|Ca|Sc|Ti|V|Cr|Mn|Fe|Co|Ni|Cu|Zn|Ga|Ge|As|Se|Br|Kr|Rb|Sr|Y|Zr|Nb|Mo|Tc|Ru|Rh|Pd|Ag|Cd|In|Sn|Sb|Te|I|Xe|Cs|Ba|La|Ce|Pr|Nd|Pm|Sm|Eu|Gd|Tb|Dy|Ho|Er|Tm|Yb|Lu|Hf|Ta|W|Re|Os|Ir|Pt|Au|Hg|Tl|Pb|Bi|Po|At|Rn|Fr|Ra|Ac|Th|Pa|U|Np|Pu|Am|Cm|Bk|Cf|Es|Fm|Md|No|Lr|Rf|Db|Sg|Bh|Hs|Mt|Ds|Rg|Cn|Nh|Fl|Mc|Lv|Ts|Og)([0-9]+)"
    return re.sub(chemical_formula_regex, r'\g<1>$_{\g<2>}$', string)

def latex_xml_tags(string):
    """Converts xml tags such as MathML or html entities like <sub> to latex"""
    string = re.sub(r"<sub>(.+?)</sub>", r'$_{\g<1>}$', string)
    string = re.sub(r"<(?:mml:)?msub><(?:mml:)?mi>(.+?)</(?:mml:)?mi><(?:mml:)?mn>(.+?)</(?:mml:)?mn></(?:mml:)?msub>", r'\g<1>$_{\g<2>}$', string)
    # removing any remaining tags from the title
    string = re.sub(r"</?(?:mml:)?(.+?)>", r'', string)
    return string


def remove_words(string, wordlist):
    return ' '.join([word for word in string.split() if word.lower() not in wordlist])


def hyphen_to_underscore(string):
    return re.sub(r'-', r'_', string)


def whitespace_to_underscore(string):
    return re.sub(r'\s', r'_', string)


def underscoreify(string):
    return re.sub(r'\W+', r'_', string)


def endash_to_hyphen(string):
    return re.sub(r'\b--\b', r'-', string)


def escape_bibtex_caps(string):
    # Rather than using (for example) "{T}est" we should do "{Test}"
    # to avoid messing with font kerning (see https://tex.stackexchange.com/a/140071)
    return re.sub(r'([\w${}\\_]*[A-Z][\w$\\{}_]*)', r'{\g<1>}', string)


def remove_breaking_characters(string):
    return re.sub(r'[\n\t*]', r'', string)


def remove_filename_breaking_characters(string):
    return re.sub(r'[~#<>$+%!`&*\'|{}?"=\\/:@.,;]', r'', string)


def process_bibtex_range(string):
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
    print_year = None
    print_month = None

    online_year = None
    online_month = None

    if 'published-print' in data:
        print_year = str(data["published-print"]['date-parts'][0][0])
        if len(data["published-print"]['date-parts'][0]) > 1:
            print_month = str(data["published-print"]['date-parts'][0][1])

    if 'published-online' in data:
        online_year = str(data["published-online"]['date-parts'][0][0])
        if len(data["published-online"]['date-parts'][0]) > 1:
            online_month = str(data["published-online"]['date-parts'][0][1])

    if print_year is None:
        return online_year, online_month

    if online_year is None:
        return print_year, print_month

    if int(print_year) < int(online_year):
        return print_year, print_month
    else:
        return online_year, online_month


def extract_pages(data, print_range=True):
    if 'page' in data:
        if print_range:
            return process_bibtex_range(data['page'])
        else:
            return data['page'].split('-')[0]
    elif 'article-number' in data:
        return data['article-number']

    return None

    raise RuntimeError("failed to extract pages")


def extract_issue(data):
    if 'issue' in data:
        return process_bibtex_range(str(data['issue']))
    return None


def extract_author(data):
    author_parts = []
    for author in data['author']:
        if "given" in author:
            author_parts.append(f'{endash_to_hyphen(encode_tex(author["family"]))}, {endash_to_hyphen(encode_tex(author["given"]))}')
        else:
            # Sometimes the crossref data is incorrect and both names have been written under "family" with nothing in
            # "given" (see 10.1038/srep01450 as an example). In this case we attempt to fix by first checking the family
            # name has more than one part and then assuming the last part is the true family name.
            names_in_family = author["family"].split()
            if len(names_in_family) > 1:
                author_parts.append(
                    f'{endash_to_hyphen(encode_tex(names_in_family[-1]))}, {endash_to_hyphen(encode_tex(" ".join(names_in_family[0:-1])))}')
            else:
                raise LookupError(f'Cannot parse author: {author}')
    return ' and '.join(author_parts)


def abbreviate_name(name, sep='.'):
    letters = re.findall(r"\b\w", name)
    return f'{sep.join(letters)}{sep}'

def unicode_authors(data):
    author_parts = []
    for author in data['author']:
        if "given" in author:
            author_parts.append(f'{endash_to_hyphen(abbreviate_name(author["given"]))} {endash_to_hyphen(author["family"])}')
        else:
            # Sometimes the crossref data is incorrect and both names have been written under "family" with nothing in
            # "given" (see 10.1038/srep01450 as an example). In this case we attempt to fix by first checking the family
            # name has more than one part and then assuming the last part is the true family name.
            names_in_family = author["family"].split()
            if len(names_in_family) > 1:
                author_parts.append(
                    f'{abbreviate_name(" ".join(names_in_family[0:-1]))} {names_in_family[-1]}')
            else:
                raise LookupError(f'Cannot parse author: {author}')

    if len(author_parts) == 1:
        author_text = author_parts[0]
    else:
        author_text = f"{', '.join(author_parts[:-1])} & {author_parts[-1]}"

    return author_text


def complex_substitution(string):
    regex = re.compile(r'(ab)\s*(initio)', flags=re.IGNORECASE)
    return regex.sub(r' \g<1> \g<2> ', string)


def extract_title(data):
    cleaned_title = escape_bibtex_caps(encode_tex(
        latex_chemical_formula(
        latex_xml_tags(
        remove_breaking_characters(
        complex_substitution(data['title'][0]))))))
    return cleaned_title.strip()


def extract_ascii_title(data):
    cleaned_title = normalise_unicode_to_ascii(remove_breaking_characters(
                complex_substitution(data['title'][0])))
    return cleaned_title.strip()

def extract_unicode_title(data):
    cleaned_title = remove_breaking_characters(
                complex_substitution(data['title'][0]))
    return cleaned_title.strip()


def extract_journal(data, abbreviate=True):
    title = data['container-title'][0]
    if abbreviate and len(title.split()) > 1:
        # Sometimes ISO-8859-1 text has been converted to UTF-8 in the crossref database producing the unicode
        # replacement character U+FFFD which we cannot resolve backwards. So we must consider the possibility
        # that some characters e.g. with umlauts are mangled (see https://en.wikipedia.org/wiki/Specials_(Unicode_block))
        return abbreviator.abbreviate(remove_words(title, {'in', 'on', 'of', 'the', 'and', 'f�r', 'für', 'und'}))
    return title


def bibtex_item(key, value):
    return f'{key}={{{encode_tex(value)}}}'


def generate_citekey(data):
    key, _ = bibdict_from_json(data)
    return key


def generate_bibtex_entry(string):
    cite_key, data = bibdict_from_json(string)
    fields = ',\n'.join([f'  {bibtex_item(k, v)}' for k, v in data['fields'].items() if v is not None])
    return (
        f"@{data['entry']}{{{cite_key},\n"
        f"{fields}\n"
        f"}}\n"
    )


def generate_short_text(data):
    if data['type'] != 'journal-article':
        raise RuntimeError('DOI is not a journal article type')

    author = data['author'][0]['family']
    journal = extract_journal(data)
    volume = data['volume']
    pages = extract_pages(data, print_range=False)
    year, _ = extract_canonical_published_date(data)

    return f"{author}, {journal} {volume}, {pages} ({year})"


def generate_long_text(data):
    if data['type'] != 'journal-article':
        raise RuntimeError('DOI is not a journal article type')

    authors = unicode_authors(data)
    journal = extract_journal(data)
    volume = data['volume']
    title = extract_unicode_title(data)
    pages = extract_pages(data, print_range=False)
    year, _ = extract_canonical_published_date(data)

    return f"{authors}, {title}, {journal} {volume}, {pages} ({year})"


def generate_markdown_text(json_entry):
    text = generate_short_text(json_entry)
    link = f'https://dx.doi.org/{json_entry["DOI"]}'
    return f'[{text}]({link})'


def generate_filename_text(json_entry):
    year, _ = extract_canonical_published_date(json_entry)
    author = json_entry['author'][0]['family']
    title = extract_ascii_title(json_entry)
    return normalise_unicode_to_ascii(remove_filename_breaking_characters(f'{year} - {author} - {title}'))


def bibdict_from_json(data):
    if data['type'] != 'journal-article':
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
    cite_key_vol = f"{bibdict['fields']['volume']}"
    cite_key_page = bibdict['fields']['pages'].split('-')[0]
    cite_key_year = bibdict['fields']['year']

    key = cite_key([cite_key_author, cite_key_journal, cite_key_vol, cite_key_page, cite_key_year])

    return key, bibdict