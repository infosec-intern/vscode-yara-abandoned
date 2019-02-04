from pathlib import Path
import unittest
from urllib.parse import quote

import helpers
import protocol


class HelperTests(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        ''' Initialize tests '''
        self.rules_path = Path(__file__).parent.joinpath("..", "test", "rules").resolve()

    def test_create_file_uri(self):
        ''' Ensure file URIs are generated from paths '''
        expected = "file:///{}".format(quote(str(self.rules_path).replace("\\", "/"), safe="/\\"))
        output = helpers.create_file_uri(str(self.rules_path))
        self.assertEqual(output, expected)

    def test_get_first_non_whitespace_index(self):
        ''' Ensure the index of the first non-whitespace is extracted from a string '''
        index = helpers.get_first_non_whitespace_index("    test")
        self.assertEqual(index, 4)

    def test_get_rule_range(self):
        ''' Ensure YARA rules are parsed out and their range is returned '''
        peek_rules = self.rules_path.joinpath("peek_rules.yara").resolve()
        rules = peek_rules.read_text()
        pos = protocol.Position(line=42, char=12)
        result = helpers.get_rule_range(rules, pos)
        self.assertIsInstance(result, protocol.Range)
        self.assertEqual(result.start.line, 33)
        self.assertEqual(result.start.char, 0)
        self.assertEqual(result.end.line, 43)
        self.assertEqual(result.end.char, 0)

    def test_parse_result(self):
        ''' Ensure the parse_result() function properly parses a given diagnostic '''
        result = "line 14: syntax error, unexpected <true>, expecting text string"
        line_no, message = helpers.parse_result(result)
        self.assertEqual(line_no, 14)
        self.assertEqual(message, "syntax error, unexpected <true>, expecting text string")

    def test_parse_result_multicolon(self):
        ''' Sometimes results have colons in the messages - ensure this doesn't affect things '''
        result = "line 15: invalid hex string \"$hex_string\": syntax error"
        line_no, message = helpers.parse_result(result)
        self.assertEqual(line_no, 15)
        self.assertEqual(message, "invalid hex string \"$hex_string\": syntax error")

    def test_parse_uri(self):
        ''' Ensure paths are properly parsed '''
        path = "c:/one/two/three/four.txt"
        file_uri = "file:///{}".format(path)
        self.assertEqual(helpers.parse_uri(file_uri), path)

    def test_resolve_symbol(self):
        ''' Ensure symbols are properly resolved '''
        document = "rule ResolveSymbol {\n strings:\n  $a = \"test\"\n condition:\n  #a > 3\n}\n"
        pos = protocol.Position(line=4, char=3)
        symbol = helpers.resolve_symbol(document, pos)
        self.assertEqual(symbol, "#a")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser("Run protocol.py tests")
    parser.add_argument("-v", dest="verbose", action="count", default=0, help="Change test verbosity")
    args = parser.parse_args()
    if args.verbose > 2:
        args.verbose = 2
    runner = unittest.TextTestRunner(verbosity=args.verbose)
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(HelperTests)
    results = runner.run(suite)
    pct_coverage = (results.testsRun - (len(results.failures) + len(results.errors))) / results.testsRun
    print("HelperTests coverage: {:.1f}%".format(pct_coverage * 100))
