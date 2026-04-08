from blib.utils import normalise_unicode_to_ascii


def article_citekey(data):
    citekey_author = normalise_unicode_to_ascii(data['author'][0]['family']).replace(' ', '').replace('-', '')
    citekey_journal = data['journal_abbreviation'].replace(' ', '').replace('.', '').replace(':', '')

    if "pages" not in data or data["pages"] is None:
        return f'{citekey_author}_{citekey_journal}_{data["volume"]}_{data["year"]}'
    else:
        return f'{citekey_author}_{citekey_journal}_{data["volume"]}_{data["pages"][0]}_{data["year"]}'



def misc_citekey(data):
    citekey_author = normalise_unicode_to_ascii(data['author'][0]['family']).replace(' ',
                                                                                      '').replace(
        '-', '')
    citekey_journal = data['eprint'].replace('.', '_')

    if "pages" not in data or data["pages"] is None:
        return f'{citekey_author}_{citekey_journal}_{data["year"]}'
    else:
        return f'{citekey_author}_{citekey_journal}_{data["pages"][0]}_{data["year"]}'
