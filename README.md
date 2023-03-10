# blib
Bibtex generator from DOI

Extracts digital object identifiers (DOIs) from strings supplied on the command line or from a file and creates well formated bibtex entries. The primary aim is to make less mistakes than Mendeley. Only tested on MacOS, some features (clipboard for rtf for example), may not work in other environments).

## Features
- Produces correct tex escape sequences for non-ascii characters in author names.
- Enforces capitalisation of words within bibtex titles. 
- Uses ISO4 to abbreviate journal names.
- Attempts to find chemical formulae and typeset the subscripts properly.
- If given a URL it will attempt to find the DOI either in the URL or from metadata on the web page

## Current Limitations
- Only handles journal bibtex entries.
- Cannot fix mistakes in the cross ref entry (e.g. italic text which gets butted up to the next word).

## Usage
usage: blib [-h] [--output {bib,txt,rtf,review}] [--clip | --no-clip]
            [--title | --no-title] [--abbrev | --no-abbrev]
            [--authors AUTHORS] [--etal ETAL]
            [doi ...]

fetch bibtex entries from a list of strings containing DOIs.

positional arguments:
  doi                   a string containing a doi

options:
  -h, --help            show this help message and exit
  --output {bib,txt,rtf,review}
                        output format (default: bib)
  --clip, --no-clip     copy results to clipboard (default: True)
  --title, --no-title   include title in output (default: True)
  --abbrev, --no-abbrev
                        abbreviate journal name in output (default: True)
  --authors AUTHORS     number of authors to include in output
  --etal ETAL           text to use for "et al"

## Output formats

### bib

A standard bibtex output:

```
@article{FernandezPacheco_NatMater_18_679_2019,
  author    = {Fern{\'a}ndez-Pacheco, Amalio and Vedmedenko, Elena and Ummelen, Fanny and Mansell, Rhodri and Petit, Doroth{\'e}e and Cowburn, Russell P.},
  title     = {{Symmetry}-breaking interlayer {Dzyaloshinskii}–{Moriya} interactions in synthetic antiferromagnets},
  journal   = {Nat. Mater.},
  issue     = {7},
  volume    = {18},
  pages     = {679--684},
  year      = {2019},
  month     = {6},
  publisher = {Springer Science and Business Media LLC},
  doi       = {10.1038/s41563-019-0386-4},
  url       = {https://dx.doi.org/10.1038/s41563-019-0386-4}
}
```

### txt

A plain text reference useful for presentations or referring to a paper in notes:

A. Fernández-Pacheco et al., Symmetry-breaking interlayer Dzyaloshinskii–Moriya interactions in synthetic antiferromagnets, Nat. Mater. 18, 679 (2019)

### rtf

A rich rext format suitable for MS Word. The clipboard contains the rtf text to paste into Word, the terminal can only display the raw rtf encoding.

A. Fernández-Pacheco *et al.*, Symmetry-breaking interlayer Dzyaloshinskii–Moriya interactions in synthetic antiferromagnets, Nat. Mater. **18**, 679 (2019)

### review

Long format rtf suitable for reviews in MS Word.

Symmetry-breaking interlayer Dzyaloshinskii–Moriya interactions in synthetic antiferromagnets, A. Fernández-Pacheco, E. Vedmedenko, F. Ummelen, R. Mansell, D. Petit, and R.P. Cowburn, Nature Materials **18**, 679 (2019); https://doi.org/10.1038/s41563-019-0386-4


