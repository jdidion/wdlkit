from pathlib import Path
from typing import Optional, Sequence
from urllib3.util import parse_url

import autoclick

from wdlkit.ast import load_document
from wdlkit.formatter import Formatter


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

    doc = load_document(uri, import_dir)

    formatted = Formatter.format_document(uri, doc)

    for uri, contents in formatted.items():
        parsed = parse_url(uri)

        if parsed.scheme not in {None, "", "file"}:
            output_file = (output_dir or Path.cwd()) / Path(parsed.path).name
        else:
            path = Path(uri)

            if output_dir:
                output_file = output_dir / path.name
            else:
                output_file = path.absolute()

        with open(output_file, "wt") as out:
            out.write(contents)


if __name__ == "__main__":
    wdlkit()
