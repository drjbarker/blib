#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import argparse
import json

from urllib.request import urlopen
from urllib.error import URLError

from tex.bibtex import generate_bibtex_entry, generate_short_text


def find_doi(string):
    """Return the first DOI in `string`. Returns `None` if no DOI is found."""
    doi_regex = r'(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?![!@#%^{}",? ])\S)+)'
    match = re.search(doi_regex, string)
    if not match:
        return None
    return match.group()


def find_arxiv_id(string):
    """Returns the first arXiv id in `string`. Return `None` if no aXiv id is found."""
    # https://arxiv.org/help/arxiv_identifier
    arxiv_id_regex = r'arxiv.*([0-9]{2}[0-1][0-9]\.[0-9]{4,}(?:v[0-9]+)?)'
    match = re.search(arxiv_id_regex, string)
    if not match:
        return None
    return match.group()


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
    with urlopen(url) as response:
        if not response.code == 200:
            raise URLError(f"failed to resolve https://api.crossref.org/works/{doi}")

        # Decode the response to a string. This *should* be a json dataset which we then
        # convert to a dictionary and return.
        return json.loads(response.read().decode('utf-8'))['message']


def format_reference(json_entry, reference_format):
    if reference_format == "bibtex":
        return generate_bibtex_entry(json_entry)

    if reference_format == "short":
        return generate_short_text(json_entry)

    raise ValueError(f'Unknown output format "{reference_format}"')


def process_doi_string(string):
    for doi in doi_candidates(string):
        try:
            return crossref_entry(doi)
        except URLError:
            continue
    else:
        raise ValueError(f'No crossref entry for any DOI candidates')


def process_doi_list(doi_list, reference_format, print_comments=False):
    for string in doi_list:
        if print_comments:
            print(f'// {string}')

        try:
            print(format_reference(process_doi_string(string), reference_format))

        except Exception as e:
            print(f'// WARNING: unable to get bibtex entry for "{string}"')
            print(f'// {e}')


def process_file(filename, reference_format, print_comments=False):
    processed_dois = set()
    with open(filename) as f:
        for line in f:
            if print_comments:
                print(f'// {line.strip()}')

            try:
                doi = find_doi(line)
                if (doi is not None) and not (doi in processed_dois):
                    print(format_reference(process_doi_string(line), reference_format))
                    processed_dois.add(doi)

            except Exception as e:
                print(f'// WARNING: unable to get bibtex entry for "{line}"')
                print(f'// {e}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='fetch bibtex entries from a list of strings containing DOIs. '
    )

    parser.add_argument('doi', nargs='*', help='a string containing a doi')

    parser.add_argument('--file', help='a file containing dois')
    parser.add_argument('--comments', action='store_true', help='print search strings as bibtex comments')

    parser.add_argument('--format', help='output format (default: %(default)s)',
                        default='bibtex', choices=['bibtex', 'short'])

    args = parser.parse_args()

    if args.doi is not None:
        process_doi_list(args.doi, args.format, args.comments)

    if args.file is not None:
        process_file(args.file, args.format, args.comments)

