WDLkit is a toolkit to simplify and accelerate development of tasks and workflows in [WDL](https://openwdl.org/).

## Dependencies

* Python 3.6+

## Installation

`$ pip install wdlkit`

## Commands

### format

Formats your WDL file(s) according to [WDLkit style](docs/style.md). This command is similar to [black](https://github.com/psf/black) in that it is highly opinionated and does not allow for configuration.

```
Usage: wdlkit format [OPTIONS] URI

  Format a WDL file and its imports.

Options:
  -i, --import-dir PATH           Directory in which to look for imports. May
                                  be specified multiple times.
  -v, --version TEXT              WDL version to generate. Currently, only 1.0
                                  is supported.
  -o, --output-dir PATH           Directory in which to output formatted WDL
                                  files. If not specified, the input files are
                                  overwritten.
  -O, --overwrite / --no-overwrite
                                  Whether to overwrite the input WDL file(s)
                                  with the reformatted versions. This option
                                  is ignored if `output_dir` is specified.
                                  Currently, this option is disabled by
                                  default because WDLkit is in development and
                                  there is a risk that this command might
                                  corrupt the WDL files. Once WDLkit reaches
                                  v1.0, this option will change to be enabled
                                  by default.
  --help                          Show this message and exit.
```
