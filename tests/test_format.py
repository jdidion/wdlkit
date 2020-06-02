from wdlkit.formatter import Formatter
from WDL import Tree


def test_simple(datadir):
    """
    Test that each document is formatted the same before and after.
    """
    uri = str(datadir["workflow.wdl"])
    doc = Tree.load(uri)
    for (_, abspath), formatted in Formatter.format_document(doc).items():
        with open(abspath, "rt") as inp:
            expected = inp.read()
        assert expected == formatted
