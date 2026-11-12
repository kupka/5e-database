# libsrd5 feat generator

Generates the racial and class feature values of the `Feat` enum in
[libsrd5](https://github.com/kupka/libsrd5) (`libsrd5/ogl/Feats.cs`) and their names and
descriptions in `FeatTextResource` (`libsrd5/ogl/TextResources.cs`).

- `gen_feats.py`: the generator.
- `gen_feats_manual.py`: decisions made by checking the SRD 5.1 PDF by hand (merged copies,
  removed feats, corrected texts). It is executed by `gen_feats.py`.

## Rules

- The list of features comes from the 5e-database JSON (Features, Traits, Races, Subraces).
- Every description is verified against the text of the official SRD 5.1 (OGL edition).
  JSON text that differs only in case, punctuation or dashes is replaced by the SRD wording;
  any other difference must be resolved in `gen_feats_manual.py`, otherwise the script stops
  and writes the open cases to `<srd text>.problems.txt`.
- Features the JSON splits into numbered or repeated copies are merged into one value.
- Double dashes and em dashes are written as ` - `.

## Usage

The JSON is read from `src/2014/en`.

```sh
# SRD 5.1 (OGL) as text
curl -LO https://media.wizards.com/2016/downloads/DND/SRD-OGL_V5.1.pdf
pdftotext SRD-OGL_V5.1.pdf srd.txt

# start from libsrd5's main versions of the two files, then generate
cd libsrd5
git show origin/main:libsrd5/ogl/Feats.cs > libsrd5/ogl/Feats.cs
git show origin/main:libsrd5/ogl/TextResources.cs > libsrd5/ogl/TextResources.cs
python3 -I path/to/gen_feats.py . path/to/5e-database/src/2014/en path/to/srd.txt
```

`Feats.cs` keeps its CRLF line endings and `TextResources.cs` its LF line endings.
