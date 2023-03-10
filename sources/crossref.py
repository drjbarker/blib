import json
import abbrev
from ltwa import LTWA_ABBREV

from urllib.request import urlopen, Request
from urllib.error import URLError

try:
    has_diskcache = True
    import diskcache as dc
except ImportError:
    has_diskcache = False

BLIB_HTTP_USER_AGENT = r'blib/0.1 (https://github.com/drjbarker/blib; mailto:j.barker@leeds.ac.uk)'

class CrossrefSource:

    def __init__(self):
        self._abbreviator = abbrev.Abbreviator(LTWA_ABBREV)
        # appears to be an error in the LTWA that report -> rep. with no consideration of reports
        self._abbreviator.remove(r'report')
        self._abbreviator.insert(r'reports?', r'rep.')
        if has_diskcache:
            self._cache = dc.Cache('tmp', size_limit=1e7) # 10 MB

    def request(self, doi, use_cache=True):
        if use_cache and has_diskcache and doi in self._cache:
            return self._cache[doi]

        # In principle this should have the best performance if we include a user-agent
        # header with a mailto: email address. This sends us to a 'polite' set of servers
        # at crossref. In reality (possibly because we are make single very small queries)
        # lookups are MUCH faster if we use no headers.

        url = f'https://api.crossref.org/works/{doi}'
        with urlopen(Request(url, headers={'User-Agent': BLIB_HTTP_USER_AGENT})) as response:
            if not response.code == 200:
                raise URLError(f"failed to resolve https://api.crossref.org/works/{doi}")

            # Decode the response to a string. This *should* be a json dataset which we then
            # convert to a dictionary and return.
            jdata = json.loads(response.read().decode('utf-8'))['message']

        if jdata['type'] != 'journal-article':
            raise RuntimeError('DOI is not a journal article type')

        # We use some private methods to normalise the data
        result = {
            'authors':        self._authors(jdata),
            'title':          self._title(jdata),
            'journal':        self._journal(jdata),
            'journal-abbrev': self._journal_abbrev(jdata),
            'doi':            self._doi(jdata),
            'url':            self._url(jdata),
            'entry':          'article',
            'issue':          self._issue(jdata),
            'volume':         self._volume(jdata),
            'pages':          self._pages(jdata),
            'publisher':      self._publisher(jdata),
            'published-date': self._published_date(jdata)}

        if has_diskcache:
            self._cache[doi] = result

        return result

    def _authors(self, jdata):
        author_list = []
        for author in jdata['author']:
            if "given" in author and "family" in author:
                given = author["given"]
                family = author["family"]
            else:
                # Sometimes the crossref data is incorrect and both names have been written under "family" with nothing in
                # "given" (see 10.1038/srep01450 as an example). In this case we attempt to fix by first checking the family
                # name has more than one part and then assuming the last part is the true family name.
                names_in_family = author["family"].split()
                if len(names_in_family) > 1:
                    given = names_in_family[0:-1]
                    family = names_in_family[-1]
                else:
                    raise LookupError(f'Cannot parse author: {author}')

            author_list.append({"given": given, "family": family})
        return author_list


    def _doi(self, jdata):
        return jdata['DOI']


    def _url(self, jdata):
        return f'https://dx.doi.org/{jdata["DOI"]}'


    def _title(self, jdata):
        return jdata['title'][0]


    def _journal(self, jdata):
        return jdata['container-title'][0]


    def _journal_abbrev(self, jdata):
        title = jdata['container-title'][0]
        remove_words = lambda text, wordlist : ' '.join([word for word in text.split() if word.lower() not in wordlist])

        if len(title.split()) > 1:
            # Sometimes ISO-8859-1 text has been converted to UTF-8 in the crossref database producing the unicode
            # replacement character U+FFFD which we cannot resolve backwards. So we must consider the possibility
            # that some characters e.g. with umlauts are mangled (see https://en.wikipedia.org/wiki/Specials_(Unicode_block))
            return self._abbreviator.abbreviate(remove_words(title, {'in', 'on', 'of', 'the', 'and', 'f�r', 'für', 'und'}))
        return title


    def _issue(self, jdata):
        if 'issue' in jdata:
            return str(jdata['issue'])
        return None

    def _volume(self, jdata):
        if 'volume' in jdata:
            return str(jdata['volume'])
        return None


    def _pages(self, jdata):
        if 'page' in jdata:
            return jdata['page'].split('-')
        elif 'article-number' in jdata:
            return [jdata['article-number']]
        return None


    def _publisher(self, jdata):
        if 'publisher' in jdata:
            return jdata['publisher']
        return None


    def _published_date(self, jdata):
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

        if 'published-print' in jdata:
            print_year = str(jdata["published-print"]['date-parts'][0][0])
            if len(jdata["published-print"]['date-parts'][0]) > 1:
                print_month = str(jdata["published-print"]['date-parts'][0][1])

        if 'published-online' in jdata:
            online_year = str(jdata["published-online"]['date-parts'][0][0])
            if len(jdata["published-online"]['date-parts'][0]) > 1:
                online_month = str(jdata["published-online"]['date-parts'][0][1])

        if print_year is None:
            return {'year': online_year, 'month': online_month}

        if online_year is None:
            return {'year': print_year, 'month': print_month}

        if int(print_year) < int(online_year):
            return {'year': print_year, 'month': print_month}
        else:
            return {'year': online_year, 'month': online_month}