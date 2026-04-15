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
usage: blib [-h] [--output {md,bib,txt,rtf,review,doi,data}] [--clip | --no-clip]
            [--title | --no-title] [--abbrev | --no-abbrev]
            [--authors AUTHORS] [--etal ETAL] [--format FORMAT] [--orcid ORCID]
            [doi ...]

fetch bibtex entries from a list of strings containing DOIs.

positional arguments:
  doi                   a string containing a doi

options:
  -h, --help            show this help message and exit
  --output {md,bib,txt,rtf,review,doi,data}
                        output format (default: bib)
  --clip, --no-clip     copy results to clipboard (default: True)
  --title, --no-title   include title in output (default: True for txt/rtf, False for md)
  --abbrev, --no-abbrev
                        abbreviate journal name in output (default: True)
  --authors AUTHORS     number of authors to include in output
  --etal ETAL           text to use for "et al"
  --format FORMAT       BibDesk autogeneration format string used by md/txt/rtf output
  --orcid ORCID         ORCID iD in the format 0000-0000-0000-0000

## Output formats

### BibDesk formatting

The `md`, `txt`, and `rtf` formatters can optionally be overridden with `--format` using the
autogeneration syntax popularized by [BibDesk](https://bibdesk.sourceforge.io/). If you want the
full original reference, see the BibDesk manual page for
[Autogeneration Format Syntax](https://bibdesk.sourceforge.io/manual/BibDeskHelp_92.html).

In blib, the format string is responsible for the whole citation string.

For example:

```sh
blib --output txt --format "%A[, ][ ]2, %t (%Y)" 10.1038/s41563-019-0386-4
```

This produces output like:

```text
Fernández-Pacheco A., Vedmedenko E., Symmetry-breaking interlayer Dzyaloshinskii-Moriya interactions in synthetic antiferromagnets (2019)
```

If you want the cite key in the output you can include it via `%f{Cite Key}`. For example:

```sh
blib --output txt --format "%A[, ][, ]1, %t. %f{Journal Abbreviation} %Y; %f{Volume}: %f{Pages}" 10.1038/s41563-019-0386-4
```

which gives a citation in the form:

```text
Fernández-Pacheco, A, Symmetry-breaking interlayer Dzyaloshinskii-Moriya interactions in synthetic antiferromagnets. Nat. Mater. 2019; 18: 679--684
```

The formatter works against blib's normalized bibliography fields, including:

- `Author`
- `Title`
- `Journal`
- `Journal Abbreviation`
- `Volume`
- `Number`
- `Pages`
- `Year`
- `Month`
- `DOI`
- `URL`
- `Cite Key`

#### Syntax overview

A format string is plain text mixed with `%` specifiers. Literal text is copied into the output and
specifiers are replaced with values derived from the reference metadata.

Many specifiers support:

- square-bracket options such as `%A[, ][ ]2`
- numeric parameters such as `%t20`
- field names inside braces such as `%f{Journal Abbreviation}`

#### Supported specifiers

These specifiers are implemented in blib today.

- `%a`
  Uses author last names. Supports optional name separator, optional `et al.` text, a maximum number of names, and for lowercase `%a` a maximum family-name length.
- `%A`
  Uses author names with initials. Supports optional name separator, optional last-name/initial separator, optional `et al.` text, and a maximum number of names.
- `%p`
  Same idea as `%a`, but prefers editors when an editor field exists and otherwise falls back to authors.
- `%P`
  Same idea as `%A`, but prefers editors when an editor field exists and otherwise falls back to authors.
- `%t`
  Inserts the title, optionally truncated to a maximum character count.
- `%T`
  Inserts title words, with an optional "ignore short words" threshold and optional maximum word count.
- `%y`
  Two-digit year.
- `%Y`
  Full year.
- `%m`
  Numeric month.
- `%k`
  Concatenated keywords, with optional slash replacement, separator, and maximum keyword count.
- `%f{Field}`
  Inserts an arbitrary field. This is also how you access values like `Cite Key` and `BibTeX Type`.
- `%w{Field}`
  Inserts words from an arbitrary field, with optional separator characters, slash replacement, output separator, and maximum word count.
- `%c{Field}`
  Builds an acronym-like form from a field.
- `%s{Field}`
  Switches between "yes", "no", or "mixed" strings depending on whether a field is empty, populated, or multi-valued.
- `%i{Key}`
  Reads a document-info key when document metadata is available in the input record.
- `%l`
  Linked-file name without extension.
- `%L`
  Linked-file name with extension.
- `%e`
  Linked-file extension including the leading dot.
- `%E`
  Linked-file extension without the leading dot, with an optional default if no extension exists.
- `%b`
  Bibliography document file name without the extension.
- `%%`, `%[`, `%]`, `%-`, `%0` ... `%9`
  Escaped literal characters for percent signs, brackets, dashes, and digits after a specifier.

#### Specifier notes

- For `%a`, `%A`, `%p`, and `%P`, a negative author count means "take authors from the end".
- For `%A` and `%P`, the second bracket option controls the separator between the surname and initials.
- For `%t`, `%T`, `%f`, `%w`, `%c`, and `%i`, a numeric value of `0` means "do not limit".
- `%f{Field}` and related field-based specifiers normalize field-name spelling, so `Journal Abbreviation`,
  `journal_abbreviation`, and similar variants resolve to the same blib field.
- For normal citation output, blib preserves readable text. In the documentation-style tests, a citekey-like
  normalization mode is also exercised so the examples line up with BibDesk's generated-key behavior.

#### Not implemented

BibDesk also defines unique-value specifiers intended for auto-generated cite keys and file names:

- `%u`
- `%U`
- `%n`

blib currently rejects these with a clear error message. They are documented in the BibDesk manual,
but are not yet part of blib's implemented subset.

#### Examples

Some useful patterns:

- `%A[, ][ ]2, %t (%Y)`
  Author initials, title, and year.
- `%A[, ][, ]1, %t. %f{Journal Abbreviation} %Y; %f{Volume}: %f{Pages}`
  A journal-style reference line.
- `[%f{Cite Key}](%f{URL})`
  A markdown link using the cite key as link text.

The documentation-based tests in the codebase cover several examples derived from the BibDesk manual.

### ORCID

You can fetch works from an ORCID record instead of supplying DOI/arXiv identifiers directly:

```sh
blib --orcid 0000-0003-4843-5516
```

The ORCID must be supplied in the form `0000-0000-0000-0000`.

When using `--orcid`, blib:

- fetches `https://pub.orcid.org/v3.0/<ORCID>/works`
- extracts at most one DOI per ORCID work group
- prefers a Crossref-sourced DOI when one is available for that work
- otherwise uses the first source in the ORCID data that exposes a DOI
- de-duplicates the resulting DOI list
- sorts the DOI list chronologically when publication dates are available

Any DOI lookups that fail are reported and processing continues. In `rtf` and `review` output these failures are
rendered as red paragraphs so they are easy to spot after pasting into a document.

### bib

A standard bibtex output:

```
@article{FernandezPacheco_NatMater_18_679_2019,
  author    = {Fern{\'a}ndez-Pacheco, Amalio and Vedmedenko, Elena and Ummelen, Fanny and Mansell, Rhodri and Petit, Doroth{\'e}e and Cowburn, Russell P.},
  title     = {{Symmetry}-breaking interlayer {Dzyaloshinskii}–{Moriya} interactions in synthetic antiferromagnets},
  journal   = {Nat. Mater.},
  number    = {7},
  volume    = {18},
  pages     = {679--684},
  year      = {2019},
  month     = {6},
  publisher = {Springer Science and Business Media LLC},
  doi       = {10.1038/s41563-019-0386-4},
  url       = {https://dx.doi.org/10.1038/s41563-019-0386-4}
}
```

### md

A markdown reference linked to the DOI:

A. Fernández-Pacheco et al., [Nat. Mater. 18, 679 (2019)](https://doi.org/10.1038/s41563-019-0386-4)

### txt

A plain text reference useful for presentations or referring to a paper in notes:

A. Fernández-Pacheco et al., Symmetry-breaking interlayer Dzyaloshinskii–Moriya interactions in synthetic antiferromagnets, Nat. Mater. 18, 679 (2019)

### rtf

A rich rext format suitable for MS Word. The clipboard contains the rtf text to paste into Word, the terminal can only display the raw rtf encoding.

A. Fernández-Pacheco *et al.*, Symmetry-breaking interlayer Dzyaloshinskii–Moriya interactions in synthetic antiferromagnets, Nat. Mater. **18**, 679 (2019)

### review

Long format rtf suitable for reviews in MS Word.

Symmetry-breaking interlayer Dzyaloshinskii–Moriya interactions in synthetic antiferromagnets, A. Fernández-Pacheco, E. Vedmedenko, F. Ummelen, R. Mansell, D. Petit, and R.P. Cowburn, Nature Materials **18**, 679 (2019); https://doi.org/10.1038/s41563-019-0386-4
