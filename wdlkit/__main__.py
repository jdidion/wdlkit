from pathlib import Path
from typing import Optional, Sequence

import autoclick

from wdlkit.ast import load_document
from wdlkit.formatter import Formatter
from wdlkit.utils import get_local_path
from wdlkit.version import version


@autoclick.group(version=version)
def wdlkit():
    pass


@wdlkit.command("format")
def format_wdl(
    uri: str,
    import_dir: Sequence[Path] = (),
    wdl_version: str = "1.0",
    output_dir: Optional[Path] = None,
    overwrite: bool = False,
):
    """
    Format a WDL file and its imports.

    Args:
        uri: Path or URI (file:// or http(s)://) to the main WDL file.
        import_dir: Directory in which to look for imports. May be specified multiple
            times.
        wdl_version: WDL version to generate. Currently, only 1.0 is supported.
        output_dir: Directory in which to output formatted WDL files. If not specified,
            the input files are overwritten.
        overwrite: Whether to overwrite the input WDL file(s) with the reformatted
            versions. This option is ignored if `output_dir` is specified. Currently,
            this option is disabled by default because WDLkit is in development and
            there is a risk that this command might corrupt the WDL files. Once
            WDLkit reaches v1.0, this option will change to be enabled by default.
    """
    if wdl_version != "1.0":
        raise ValueError("Only WDL v1.0 is supported currently")

    import_dir_set = set(import_dir)
    import_dir_set.add(get_local_path(uri).parent)

    doc = load_document(uri, import_dir)

    formatted = Formatter.format_document(uri, doc)

    for uri, contents in formatted.items():
        with open(get_local_path(uri, output_dir, overwrite), "wt") as out:
            out.write(contents)


if __name__ == "__main__":
    wdlkit()
