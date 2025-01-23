BLIB_HTTP_USER_AGENT = r'blib/0.1 (https://github.com/drjbarker/blib; mailto:j.barker@leeds.ac.uk)'

import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.error import URLError
from urllib.request import Request, urlopen

from blib.providers.provider import Provider

try:
    has_diskcache = True
    import diskcache as dc
except ImportError:
    has_diskcache = False


class ArxivProvider(Provider):

    def __init__(self):
        self.ns = {"atom": "http://www.w3.org/2005/Atom"}
        ET.register_namespace("", self.ns["atom"])

        if has_diskcache:
            self._cache = dc.Cache('tmp', size_limit=1e7) # 10 MB

    def request(self, arxiv_id, use_cache=True):
        if use_cache and has_diskcache and arxiv_id in self._cache:
            return self._cache[arxiv_id]

        # In principle this should have the best performance if we include a user-agent
        # header with a mailto: email address. This sends us to a 'polite' set of servers
        # at crossref. In reality (possibly because we are make single very small queries)
        # lookups are MUCH faster if we use no headers.

        url = f'http://export.arxiv.org/api/query?id_list={arxiv_id.removeprefix("arxiv.")}&start=0&max_results=1'
        with urlopen(Request(url, headers={'User-Agent': BLIB_HTTP_USER_AGENT})) as response:
            if not response.code == 200:
                raise URLError(f"failed to resolve {url}")

            # Decode the response to a string and load the xml into ET
            # print(response.read().decode('utf-8'))
            root = ET.fromstring(response.read().decode('utf-8'))


        # We use some private methods to normalise the data
        result = {
            'entry':          'misc',
            'authors':        self._authors(root),
            'title':          self._title(root),
            'journal':        self._journal(root),
            'url':            self._url(root),
            'eprint':         arxiv_id.removeprefix("arxiv."),
            'published-date': self._published_date(root),
            'archiveprefix': 'arXiv',
            'primaryclass': self._category(root),
        }

        if has_diskcache:
            self._cache[arxiv_id] = result

        return result


    def _authors(self, root):
        author_list = []
        for author in root.findall('atom:entry/atom:author/atom:name', namespaces=self.ns):
            names = author.text.split()
            given = ' '.join(names[0:-1])
            family = names[-1]

            author_list.append({"given": given, "family": family})
        return author_list

    def _id(self, root):
        arxiv_id = root.find('atom:entry/atom:id', namespaces=self.ns).text
        return arxiv_id.removeprefix('http://arxiv.org/abs/')

    def _url(self, root):
        return root.find('atom:entry/atom:link', namespaces=self.ns).attrib['href']


    def _title(self, root):
        return root.find('atom:entry/atom:title', namespaces=self.ns).text


    def _category(self, root):
        return root.find('atom:entry/atom:category', namespaces=self.ns).attrib['term']


    def _journal(self, root):
        category = root.find('atom:entry/atom:category', namespaces=self.ns).attrib['term']
        return f'arXiv.{self._id(root)} [{self._category(root)}]'


    def _published_date(self, root):
        iso_string = str(root.find('atom:entry/atom:published', namespaces=self.ns).text)
        # Python versions < 3.11 don't handle the timezone suffix so we remove it
        date = datetime.fromisoformat(iso_string.removesuffix('Z'))
        return {'year': date.year, 'month': date.month}