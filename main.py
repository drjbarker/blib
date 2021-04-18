#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import requests
import argparse
from urllib.request import urlopen
from urllib.error import URLError

from tex.bibtex import generate_bibtex_entry

BLIB_HTTP_USER_AGENT = r'blib/0.1 (https://github.com/drjbarker/blib; mailto:j.barker@leeds.ac.uk)'

def find_doi(string):
    """
    Returns the first DOI in a string. If no DOI is found it raises a ValueError.
    """
    doi_regex = r'(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?![!@#%^{}",? ])\S)+)'
    match = re.search(doi_regex, string)
    if not match:
        return None
    return match.group()


def find_arxiv_id(string):
    """
    Returns the first arXiv id in a string. If no DOI is found it raises a ValueError.

    See: https://arxiv.org/help/arxiv_identifier
    """
    arxiv_id_regex = r'arxiv.*([0-9]{2}[0-1][0-9]\.[0-9]{4,}(?:v[0-9]+)?)'
    match = re.search(arxiv_id_regex, string)
    if not match:
        return None
    return match.group()


def doi_org_json_request(doi):
    """
    Requests the json for a DOI from doi.org.
    If the doi is not found it raises the returned HTTP status error from the response library.
    """

    # In principle this should have the best performance if we include a user-agent
    # header with a mailto: email address. This sends us to a 'polite' set of servers
    # at crossref. In reality (possibly because we are make single very small queries)
    # lookups are MUCH faster if we use no headers.

    url = f'https://api.crossref.org/works/{doi}'
    with urlopen(url) as response:
        if not response.code == 200:
            raise URLError(f"failed to resolve https://api.crossref.org/works/{doi}")
        data = response.read().decode('utf-8')

    return data


def bibtex_entry_from_doi(string):
    # It's possible we have a URL with some junk on the end which cannot be distinguished from a DOI
    # Example: https://iopscience.iop.org/article/10.1088/0953-8984/28/47/476007/meta where the DOI is
    #          10.1088/0953-8984/28/47/476007 but the doi suffix is allowed to contain non-numeric characters
    #          so we can't guarantee that the "meta" is not part of the DOI. The doiRegex function will give
    #          us "10.1088/0953-8984/28/47/476007/meta".
    # The solution below is to chomp backwards on "/" looking for a match until we have only the suffix and one prefix.
    # This might be slow if there is a lot of junk on the end because we do a http request every time

    doi = find_doi(string)

    if doi is None:
        raise ValueError(f'failed to find DOI in: {string}')

    split_doi = doi.split("/")

    for n in range(len(split_doi), 1, -1):
        trial_doi = "/".join(split_doi[0:n])
        try:
            return generate_bibtex_entry(doi_org_json_request(trial_doi))
        except requests.exceptions.HTTPError:
            # likely a 404 error because the DOI does not exist
            continue

    raise ValueError(f'failed to resolve DOI on doi.org: {trial_doi}')


def process_doi_list(doi_list, print_comments=False):
    for string in doi_list:
        try:
            if print_comments:
                print(f'// {string.strip()}')
            print(bibtex_entry_from_doi(string))
        except Exception as e:
            print(f'// WARNING: unable to get bibtex entry for "{string}"\n')
            print(f'// {e}')
            pass

def process_file(filename, print_comments=False):
    processed_dois = {}
    with open(filename) as f:
        for line in f:
            if print_comments:
                print(f'// {line.strip()}')
            try:
                doi = find_doi(line)
                if (doi is not None) and not (doi in processed_dois):
                    print(bibtex_entry_from_doi(line))
                    processed_dois[doi] = ''
            except Exception as e:
                print(f'// WARNING: unable to get bibtex entry for "{line}"\n')
                print(f'// {e}')
                pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='fetch bibtex entries from a list of strings containing DOIs. '
    )

    parser.add_argument('doi', nargs='*', help='a string containing a doi')

    parser.add_argument('--file', help='a file containing dois')
    parser.add_argument('--comments', action='store_true', help='print search strings as bibtex comments')

    args = parser.parse_args()

    if args.doi is not None:
        process_doi_list(args.doi, args.comments)

    if args.file is not None:
        process_file(args.file, args.comments)

