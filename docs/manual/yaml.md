
## General

### Caveats and gotchas

#### Anchor defined in the same mapping is not resolved

#### YAML syntax clashes with python format string field-demarcation literals for implicit string scalars

### Tips and tricks

#### Add custom section with anchors for use in the available rendered sections

Can add anything to the configiration, but to maintain some consistency accross
the userbase, we suggest using a section named `custom` and having it be a
mapping, where the keys have the same name as the anchor or something similar.

```yaml title="Example"
custom:
  stations: &stations [aaaa, bbbb, cccc, dddd]

sources:

- (...)
  filenames: ['{station}.crx']
  parameters:
    station: *stations

```

## Usage in AutoBernese

### Available anchors/aliases in the core configuration

### Special tags and their constructors

#### DateRange

#### AsGPSDate

#### StringTransform

#### Path

#### PathStr

#### Parent
