# blib
Bibtex generator from DOI

Extracts digital object identifiers (DOIs) from strings supplied on the command line or from a file and creates well formated bibtex entries. The primary aim is to make less mistakes than Mendeley.

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
blib [-h] [--file FILE] [--comments] [doi ...]

fetch bibtex entries from a list of strings containing DOIs.

positional arguments:
  doi          a string containing a doi

optional arguments:
  -h, --help               show this help message and exit
  --file FILE              a file containing dois
  --comments               print search strings as bibtex comments
  --format {bibtex, short, long, md, filename} selects output format

## Output formats

### bibtex

A standard bibtex output:

```
@article{2019_Fernandez_Pacheco_NatMater_18_7,
  author={Fern{\'a}ndez-Pacheco, Amalio and Vedmedenko, Elena and Ummelen, Fanny and Mansell, Rhodri and Petit, Doroth{\'e}e and Cowburn, Russell P.},
  title={{Symmetry}-breaking interlayer {Dzyaloshinskii}--{Moriya} interactions in synthetic antiferromagnets},
  journal={Nat. Mater.},
  volume={18},
  issue={7},
  pages={679--684},
  year={2019},
  month={6},
  publisher={Springer Science and Business Media LLC},
  doi={10.1038/s41563-019-0386-4},
  url={https://dx.doi.org/10.1038/s41563-019-0386-4}
}
```

### short

A short plain text reference useful for presentations or referring to a paper in notes:

```
Fernández-Pacheco, Nat. Mater. 18, 679 (2019)
```


### long

A long plain text reference useful when grant applications ask for publications to be listed with all authors (we always abbreviate forenames to save space):

```
A. Fernández-Pacheco, E. Vedmedenko, F. Ummelen, R. Mansell, D. Petit & R.P. Cowburn, Symmetry-breaking interlayer Dzyaloshinskii–Moriya interactions in synthetic antiferromagnets, Nat. Mater. 18, 679 (2019)
```

### md

A markdown link which uses the short reference as the text with a link to the DOI:

```
[Fernández-Pacheco, Nat. Mater. 18, 679 (2019)](https://dx.doi.org/10.1038/s41563-019-0386-4)
```

### filename

A string to use for the filename which is only ascii and has had any special characters which might disturb the filesytem removed. We make no assumptions about the maximum length allowed for filenames and so use the full title:

```
2019 - Fernandez-Pacheco - Symmetry-breaking interlayer DzyaloshinskiiMoriya interactions in synthetic antiferromagnets
```


