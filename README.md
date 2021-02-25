# blib
Bibtex generator from DOI

Extracts digital object identifiers (DOIs) from strings supplied on the command line or from a file and creates well formated bibtex entries. The primary aim is to make less mistakes than Mendeley.

## Features
- Produces correct tex escape sequences for non-ascii characters in author names.
- Enforces capitalisation of words within bibtex titles. 
- Uses ISO4 to abbreviate journal names.
- Attempts to find chemical formulae and typeset the subscripts properly.

## Current Limitations
- Only handles journal bibtex entries.
- Cannot fix mistakes in the cross ref entry (e.g. italic text which gets butted up to the next word).

## Usage
blib [-h] [--file FILE] [--comments] [doi ...]

fetch bibtex entries from a list of strings containing DOIs.

positional arguments:
  doi          a string containing a doi

optional arguments:
  -h, --help   show this help message and exit
  --file FILE  a file containing dois
  --comments   print search strings as bibtex comments
