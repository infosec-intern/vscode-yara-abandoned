import asyncio
import json
from pathlib import Path
import unittest

from yarals import protocol


class ProtocolTests(unittest.TestCase):
    def test_diagnostic(self):
        ''' Ensure Diagnostic is properly encoded to JSON dictionaries '''
        pos_dict = {"line": 10, "character": 15}
        pos = protocol.Position(line=pos_dict["line"], char=pos_dict["character"])
        rg_dict = {"start": pos_dict, "end": pos_dict}
        rg = protocol.Range(start=pos, end=pos)
        diag_dict = {
            "message": "Test Diagnostic",
            "range": rg_dict,
            "relatedInformation": [],
            "severity": 1
        }
        diag = protocol.Diagnostic(
            locrange=rg,
            message=diag_dict["message"],
            severity=diag_dict["severity"]
        )
        self.assertEqual(json.dumps(diag, cls=protocol.JSONEncoder), json.dumps(diag_dict))

    def test_completionitem(self):
        ''' Ensure CompletionItem is properly encoded to JSON dictionaries '''
        comp_dict = {"label": "test", "kind": protocol.CompletionItemKind.CLASS}
        comp = protocol.CompletionItem(label=comp_dict["label"], kind=comp_dict["kind"])
        self.assertEqual(json.dumps(comp, cls=protocol.JSONEncoder), json.dumps(comp_dict))

    def test_location(self):
        ''' Ensure Location is properly encoded to JSON dictionaries '''
        pos_dict = {"line": 10, "character": 15}
        pos = protocol.Position(line=pos_dict["line"], char=pos_dict["character"])
        rg_dict = {"start": pos_dict, "end": pos_dict}
        rg = protocol.Range(start=pos, end=pos)
        loc_dict = {"range": rg_dict, "uri": "fake:///one/two/three/four.path"}
        loc = protocol.Location(
            locrange=rg,
            uri=loc_dict["uri"]
        )
        self.assertEqual(json.dumps(loc, cls=protocol.JSONEncoder), json.dumps(loc_dict))

    def test_position(self):
        ''' Ensure Position is properly encoded to JSON dictionaries '''
        pos_dict = {"line": 10, "character": 15}
        pos = protocol.Position(line=pos_dict["line"], char=pos_dict["character"])
        self.assertEqual(json.dumps(pos, cls=protocol.JSONEncoder), json.dumps(pos_dict))

    def test_range(self):
        ''' Ensure Range is properly encoded to JSON dictionaries '''
        pos_dict = {"line": 10, "character": 15}
        pos = protocol.Position(line=pos_dict["line"], char=pos_dict["character"])
        rg_dict = {"start": pos_dict, "end": pos_dict}
        rg = protocol.Range(
            start=pos,
            end=pos
        )
        self.assertEqual(json.dumps(rg, cls=protocol.JSONEncoder), json.dumps(rg_dict))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser("Run protocol.py tests")
    parser.add_argument("-v", dest="verbose", action="count", default=0, help="Change test verbosity")
    args = parser.parse_args()
    if args.verbose > 2:
        args.verbose = 2
    runner = unittest.TextTestRunner(verbosity=args.verbose)
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(ProtocolTests)
    results = runner.run(suite)
    pct_coverage = (results.testsRun - (len(results.failures) + len(results.errors))) / results.testsRun
    print("ProtocolTests coverage: {:.1f}%".format(pct_coverage * 100))
