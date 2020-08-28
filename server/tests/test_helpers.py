''' Tests for yarals.helpers module '''
from urllib.parse import quote

import pytest
from yarals import helpers, protocol


@pytest.mark.helpers
def test_create_file_uri(test_rules):
    ''' Ensure file URIs are generated from paths '''
    test_rule_path = str(test_rules)
    expected = "file:///{}".format(quote(test_rule_path.replace("\\", "/"), safe="/\\"))
    output = helpers.create_file_uri(test_rule_path)
    assert output == expected

@pytest.mark.helpers
def test_get_first_non_whitespace_index():
    ''' Ensure the index of the first non-whitespace is extracted from a string '''
    index = helpers.get_first_non_whitespace_index("    test")
    assert index == 4

@pytest.mark.helpers
def test_get_rule_range(test_rules):
    ''' Ensure YARA rules are parsed out and their range is returned '''
    peek_rules = test_rules.joinpath("peek_rules.yara").resolve()
    rules = peek_rules.read_text()
    pos = protocol.Position(line=42, char=12)
    result = helpers.get_rule_range(rules, pos)
    assert isinstance(result, protocol.Range) is True
    assert result.start.line == 33
    assert result.start.char == 0
    assert result.end.line == 43
    assert result.end.char == 0

@pytest.mark.helpers
def test_parse_result():
    ''' Ensure the parse_result() function properly parses a given diagnostic '''
    result = "line 14: syntax error, unexpected <true>, expecting text string"
    line_no, message = helpers.parse_result(result)
    assert line_no == 14
    assert message == "syntax error, unexpected <true>, expecting text string"

@pytest.mark.helpers
def test_parse_result_multicolon():
    ''' Sometimes results have colons in the messages - ensure this doesn't affect things '''
    result = "line 15: invalid hex string \"$hex_string\": syntax error"
    line_no, message = helpers.parse_result(result)
    assert line_no == 15
    assert message == "invalid hex string \"$hex_string\": syntax error"

@pytest.mark.helpers
@pytest.mark.skipif('sys.platform == "win32"')
def test_parse_uri():
    ''' Ensure paths are properly parsed '''
    path = "c:/one/two/three/four.txt"
    file_uri = "file:///{}".format(path)
    # leading forward slash should be added for non-Windows systems
    assert helpers.parse_uri(file_uri) == "/{}".format(path)

@pytest.mark.helpers
@pytest.mark.skipif('sys.platform != "win32"')
def test_parse_uri_windows():
    ''' Ensure paths are properly parsed for Windows '''
    path = "c:/one/two/three/four.txt"
    # on Windows, Python will capitalize the drive letter and use opposite slashes as everywhere else
    expected = "C:\\one\\two\\three\\four.txt"
    file_uri = "file:///{}".format(path)
    assert helpers.parse_uri(file_uri) == expected

@pytest.mark.helpers
def test_resolve_symbol():
    ''' Ensure symbols are properly resolved '''
    document = "rule ResolveSymbol {\n strings:\n  $a = \"test\"\n condition:\n  #a > 3\n}\n"
    pos = protocol.Position(line=4, char=4)
    symbol = helpers.resolve_symbol(document, pos)
    assert symbol == "#a"
