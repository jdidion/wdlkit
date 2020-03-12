from pathlib import Path
from typing import Optional, Sequence

import autoclick

from wdlkit.ast import load_document
from wdlkit.formatter import Formatter
from wdlkit.utils import get_local_path


@autoclick.group()
def wdlkit():
    pass


@wdlkit.command("format")
def format_wdl(
    uri: str,
    import_dir: Sequence[Path] = (),
    version: str = "1.0",
    output_dir: Optional[Path] = None,
):
    if version != "1.0":
        raise ValueError("Only WDL v1.0 is supported currently")

    import_dir_set = set(import_dir)
    import_dir_set.add(get_local_path(uri).parent)

    doc = load_document(uri, import_dir)

    formatted = Formatter.format_document(uri, doc)

    for uri, contents in formatted.items():
        with open(get_local_path(uri, output_dir), "wt") as out:
            out.write(contents)


if __name__ == "__main__":
    wdlkit()
