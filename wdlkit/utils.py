from pathlib import Path
from typing import Optional
from urllib3.util import parse_url


def get_local_path(
    uri: str, parent: Optional[Path] = None, overwrite: bool = True
) -> Path:
    parsed = parse_url(uri)

    if parsed.scheme not in {None, "", "file"}:
        return (parent or Path.cwd()) / Path(parsed.path).name
    else:
        path = Path(uri)

        if parent:
            return parent / path.name
        elif overwrite:
            return path.absolute()
        else:
            raise ValueError(f"Cannot overwrite local path {uri}")
