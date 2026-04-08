from blib.utils import normalise_unicode_to_ascii


def article_citekey(data):
    authors = data.get('author', data.get('authors'))
    citekey_author = normalise_unicode_to_ascii(authors[0]['family']).replace(' ', '').replace('-', '')
    journal = data.get('journal_abbreviation', data.get('journal-abbrev', data['journal']))
    citekey_journal = journal.replace(' ', '').replace('.', '').replace(':', '')
    year = _year(data)

    if "pages" not in data or data["pages"] is None:
        return f'{citekey_author}_{citekey_journal}_{data["volume"]}_{year}'
    else:
        return f'{citekey_author}_{citekey_journal}_{data["volume"]}_{data["pages"][0]}_{year}'



def misc_citekey(data):
    authors = data.get('author', data.get('authors'))
    citekey_author = normalise_unicode_to_ascii(authors[0]['family']).replace(' ', '').replace('-', '')
    citekey_journal = data['eprint'].replace('.', '_')
    year = _year(data)

    if "pages" not in data or data["pages"] is None:
        return f'{citekey_author}_{citekey_journal}_{year}'
    else:
        return f'{citekey_author}_{citekey_journal}_{data["pages"][0]}_{year}'


def _year(data):
    published_date = data.get('published-date')
    if published_date:
        return published_date['year']
    return data['year']
