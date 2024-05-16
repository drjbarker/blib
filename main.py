#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import argparse
import json
import mimetypes
import subprocess
import sys

from exception import DoiTypeError
from sources.crossref import CrossrefSource
from formatting.bibtex import BibtexFormatter
from formatting.text_formatter import TextFormatter
from formatting.richtext import RichTextFormatter
from formatting.richtext_review import RichTextReviewFormatter

from urllib.request import urlopen, Request
from urllib.error import URLError
from urllib.parse import urlparse
from html.parser import HTMLParser

try:
    has_pdfplumber = True
    import pdfplumber
except ImportError:
    has_pdfplumber = False

BLIB_HTTP_USER_AGENT = r'blib/0.1 (https://github.com/drjbarker/blib; mailto:j.barker@leeds.ac.uk)'


def is_url(string):
    try:
        result = urlparse(string)
        return True
    except ValueError:
        return False

def find_doi(string):
    """Return the first DOI in `string`. Returns `None` if no DOI is found."""
    doi_regex = r'(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?![!@#%^{}",? ])\S)+)'
    match = re.search(doi_regex, string)
    if not match:
        return None
    return match.group()

def find_all_doi(string):
    """Return all the DOIs in `string`. Returns `None` if no DOI is found."""
    doi_regex = r'(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?![!@#%^{}",? ])\S)+)'
    match = re.finditer(doi_regex, string)
    if not match:
        return None
    return [x.group() for x in match]


def find_arxiv_id(string):
    """Returns the first arXiv id in `string`. Return `None` if no aXiv id is found."""
    # https://arxiv.org/help/arxiv_identifier
    arxiv_id_regex = r'arxiv.*([0-9]{2}[0-1][0-9]\.[0-9]{4,}(?:v[0-9]+)?)'
    match = re.search(arxiv_id_regex, string)
    if not match:
        return None
    return match.group()


class HTMLDOIMetaParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'meta':
            attrs_dict = dict(attrs)
            if 'name' in attrs_dict:
                if attrs_dict['name'] in ('citation_doi', 'DOI', 'dc.identifier'):
                    self.doi = attrs_dict['content']


def doi_from_webpage_meta_data(url):
    """
    Return the DOI contained in meta tags on the webpage at the `url`. Return `None` if no DOI information is found.

    Many publishers include the DOI as part of the URL. In this case we can simply find the DOI from the URL string. If
    the DOI is not explicitly included in the URL we can still often find the DOI by loading the URL and reading the
    meta data tags in the HTML head section. These are put in by the publishers to help Google Scholar to index the
    data. For example:

        <meta name="citation_doi" content="10.1038/s41586-020-2012-7">

    So we will try to read from this.

    Some publishers don't like automated access of webpages and will block accesses with a captcha. It seems to be most
    common for publishers who do already have the DOI in the URL so returning that DOI first works in most cases.
    """

    # If the url contains a valid DOI then return this. This will help us avoid annoying some services (e.g. IOP) which
    # will otherwise block us with a captcha for automated access of the webpage.
    doi = find_doi(url)
    if doi:
        return doi

    try:
        with urlopen(Request(url, headers={'User-Agent': BLIB_HTTP_USER_AGENT})) as response:
            # Decode the response to a string. This *should* be a json dataset which we then
            # convert to a dictionary and return.
            parser = HTMLDOIMetaParser()

            html = response.read().decode('utf-8')

            parser.feed(html)

            if parser.doi:
                return parser.doi
    except ValueError:
        return None

    return None


def doi_candidates(string):
    """
    Find the first doi in `string` and return a list of potentially valid doi strings ordered from longest to
    shortest.
    """
    # It's possible we have a URL with some junk on the end which cannot be distinguished from a DOI
    # Example: https://iopscience.iop.org/article/10.1088/0953-8984/28/47/476007/meta where the DOI is
    #          10.1088/0953-8984/28/47/476007 but the doi suffix is allowed to contain non-numeric characters
    #          so we can't guarantee that the "meta" is not part of the DOI. The doiRegex function will give
    #          us "10.1088/0953-8984/28/47/476007/meta".
    # The solution below is to chomp backwards on "/" looking for a match until we have only the suffix and one prefix.
    # This might be slow if there is a lot of junk on the end because we do a http request every time
    doi = find_doi(string)

    if doi is None:
        doi = doi_from_webpage_meta_data(string)
        if doi is None:
            raise ValueError(f'Not a valid DOI: "{string}"')

    split_doi = doi.split("/")
    return ["/".join(split_doi[0:n]) for n in range(len(split_doi), 1, -1)]


def crossref_entry(doi):
    """
    Return crossref database entry for `doi` from crossref.org as dictionary.

    Raises URLError if `doi` is not found on crossref.org.
    """

    # In principle this should have the best performance if we include a user-agent
    # header with a mailto: email address. This sends us to a 'polite' set of servers
    # at crossref. In reality (possibly because we are make single very small queries)
    # lookups are MUCH faster if we use no headers.

    url = f'https://api.crossref.org/works/{doi}'
    with urlopen(Request(url, headers={'User-Agent' : BLIB_HTTP_USER_AGENT})) as response:
        if not response.code == 200:
            raise URLError(f"failed to resolve https://api.crossref.org/works/{doi}")

        # Decode the response to a string. This *should* be a json dataset which we then
        # convert to a dictionary and return.
        return json.loads(response.read().decode('utf-8'))['message']


def process_doi_string(string):
    for doi in doi_candidates(string):
        try:
            return crossref_entry(doi)
        except URLError:
            continue
    else:
        raise ValueError(f'No crossref entry for any DOI candidates')

def find_doi_from_metadata(filename):
    # https://exiftool.org/examples.html
    if sys.platform.startswith('darwin'):
        p = subprocess.Popen(['mdls', '-name', 'kMDItemKeywords', '-name', 'kMDItemWhereFroms', filename], stdout=subprocess.PIPE)
        for line in p.stdout.readlines():
            if doi := find_doi(line.decode()): return doi

    p = subprocess.Popen(['pdfinfo', filename], stdout=subprocess.PIPE)
    for line in p.stdout.readlines():
        if doi := find_doi(line.decode()): return doi

    p = subprocess.Popen(['exiftool', '-keywords', '-MDItemWhereFroms', filename], stdout=subprocess.PIPE)
    for line in p.stdout.readlines():
        if doi := find_doi(line.decode()): return doi


def find_doi_from_pdf(filename, num_pages=2):
    """
    Attempts to find a DOI from a pdf file.

    This first checks the file metadata for a DOI. If none is found then it opens the pdf and checks the pdf metadata
    for a DOI. If no DOI is found then it scrapes the text on the first `num_pages`
    for DOIs. In all cases the first DOI found is returned.

    :param filename:
    :return:
    """

    # First attempt to find a DOI in the file metadata. Quite a few publishers include the DOI as a keyword and
    # on macOS we can often find the URL the pdf was downloaded from via MDItemWhereFroms which may have the
    # DOI encoded. Searching file metadata is much faster than scraping the pdf below!
    if doi := find_doi_from_metadata(filename): return doi

    if has_pdfplumber:
        with pdfplumber.open(filename) as pdf:
            # In modern PDFs the DOI of the document is often found in the pdf metadata. There's no standard for
            # key names, so we simply check all the key value pairs in the metadata. This should be much faster
            # than scraping the pdf.
            for key, value in pdf.metadata.items():
                doi = find_doi(value)
                if doi:
                    return doi

            # Check the first `num_pages` of text
            for page in pdf.pages[:min(num_pages, len(pdf.pages))]:
                pdf_text = page.extract_text()
                doi = find_doi(pdf_text)
                if doi:
                    return doi

def copy_to_clipboard(text):
    if sys.platform.startswith('darwin'):
        p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
        p.communicate(input=text.encode('utf-8'))
    elif sys.platform.startswith('linux'):
        p = subprocess.Popen(['xclip', '-selection', 'c'], stdin=subprocess.PIPE)
        p.communicate(input=text.encode('utf-8'))
    # elif sys.platform.startswith('win32'):
    #
    # else:
    #     raise RuntimeError(f"unsupported clipboard platform {sys.platform}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='fetch bibtex entries from a list of strings containing DOIs. '
    )

    parser.add_argument('doi', nargs='*', help='a string containing a doi')

    parser.add_argument('--output', help='output format (default: %(default)s)',
                        default='bib', choices=['bib', 'txt', 'rtf', 'review'])

    parser.add_argument('--clip', action=argparse.BooleanOptionalAction, help='copy results to clipboard',
                        default=True)

    parser.add_argument('--title', action=argparse.BooleanOptionalAction, help='include title in output',
                        default=True)

    parser.add_argument('--abbrev', action=argparse.BooleanOptionalAction, help='abbreviate journal name in output',
                        default=True)

    parser.add_argument('--authors', type=int, help='number of authors to include in output',
                        default=1)

    parser.add_argument('--etal', type=str, help='text to use for "et al"',
                        default = "et al.")


    args = parser.parse_args()

    doi_list = []

    for item in args.doi:
        # check if the item is a file or a plain string
        if os.path.isfile(os.path.expanduser(item)):
            filepath = os.path.expanduser(item)
            mimetype, _ = mimetypes.guess_type(filepath)
            if (mimetype == 'application/pdf') or (mimetype == 'application/x-pdf'):
                # file is a pdf file
                if doi := find_doi_from_pdf(filepath): doi_list.append(doi)
            else:
                # assume file is a text file
                with open(filepath) as f:
                    for line in f:
                        doi_list += find_all_doi(line)
        elif is_url(item):
            if doi := doi_from_webpage_meta_data(item): doi_list.append(doi)
        else:
            if doi := find_doi(item): doi_list.append(doi)

    if args.output == 'bib':
        formatter = BibtexFormatter(
            abbreviate_journals=args.abbrev,
            use_title=args.title,
            max_authors=args.authors,
            etal=args.etal
        )
    elif args.output == 'txt':
        formatter = TextFormatter(
            abbreviate_journals=args.abbrev,
            use_title=args.title,
            max_authors=args.authors,
            etal=args.etal
        )
    elif args.output == 'rtf':
        formatter = RichTextFormatter(
            abbreviate_journals=args.abbrev,
            use_title=args.title,
            max_authors=args.authors,
            etal=args.etal
        )
    elif args.output == 'review':
        formatter = RichTextReviewFormatter(
        )


    source = CrossrefSource()

    results = [formatter.header()]
    for doi in doi_list:
        try:
            text = formatter.format(source.request(doi))
            if text:
                results.append(text)
        except (DoiTypeError, URLError) as e:
            results.append(f'\n// {e}\n\n')

    results.append(formatter.footer())

    if args.clip:
        copy_to_clipboard(''.join(results))

    print(''.join(results))

