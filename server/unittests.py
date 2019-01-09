import asyncio
import json
import logging
from pathlib import Path
import socket
import unittest
from urllib.parse import quote

import helpers
import protocol
import server


class YaraLanguageServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        ''' Initialize tests '''
        self.rules_path = Path(__file__).parent.joinpath("..", "test", "rules").resolve()
        self.server = server.YaraLanguageServer()
        self.server_address = "127.0.0.1"
        self.server_port = 8471

    def setUp(self):
        ''' Create a new loop and server for each test '''
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    @classmethod
    def tearDownClass(self):
        ''' Clean things up '''
        pass

    def tearDown(self):
        ''' Shut down the server created for this test '''
        if self.loop.is_running():
            self.loop.stop()
        if not self.loop.is_closed():
            self.loop.close()

    #### CONFIG TESTS ####
    def test_config_compile_on_save_false(self):
        ''' Ensure documents are not compiled on save when false '''
        change_config_request = {
            "jsonrpc":"2.0",
            "method": "workspace/didChangeConfiguration",
            "params": {
                "settings": {
                    "yara": {"compile_on_save": False}
                }
            }
        }
        save_file = str(self.rules_path.joinpath("simple_mistake.yar").resolve())
        save_request = {
            "jsonrpc": "2.0",
            "method":"textDocument/didSave",
            "params": {
                "textDocument": {
                    "uri": helpers.create_file_uri(save_file),
                    "version": 2
                }
            }
        }
        self.assertFalse(True)

    def test_config_compile_on_save_true(self):
        ''' Ensure documents are compiled on save when true '''
        change_config_request = {
            "jsonrpc":"2.0",
            "method": "workspace/didChangeConfiguration",
            "params": {
                "settings": {
                    "yara": {"compile_on_save": True}
                }
            }
        }
        save_file = str(self.rules_path.joinpath("simple_mistake.yar").resolve())
        save_request = {
            "jsonrpc": "2.0",
            "method":"textDocument/didSave",
            "params": {
                "textDocument": {
                    "uri": helpers.create_file_uri(save_file),
                    "version": 2
                }
            }
        }
        self.assertTrue(False)

    def test_config_require_imports_false(self):
        ''' Ensure all code completion suggestions are sent when false '''
        change_config_request = {
            "jsonrpc":"2.0",
            "method": "workspace/didChangeConfiguration",
            "params": {
                "settings": {
                    "yara": {"require_imports": False}
                }
            }
        }
        self.assertFalse(True)

    def test_config_require_imports_true(self):
        ''' Ensure only imported modules are suggested when true '''
        change_config_request = {
            "jsonrpc":"2.0",
            "method": "workspace/didChangeConfiguration",
            "params": {
                "settings": {
                    "yara": {"require_imports": True}
                }
            }
        }
        self.assertTrue(False)

    #### HELPER.PY TESTS ####
    def test_helper_create_file_uri(self):
        ''' Ensure file URIs are generated from paths '''
        expected = "file:///{}".format(quote(str(self.rules_path).replace("\\", "/"), safe="/\\"))
        output = helpers.create_file_uri(str(self.rules_path))
        self.assertEqual(output, expected)

    def test_helper_get_first_non_whitespace_index(self):
        ''' Ensure the index of the first non-whitespace is extracted from a string '''
        index = helpers.get_first_non_whitespace_index("    test")
        self.assertEqual(index, 4)

    def test_helper_get_rule_range(self):
        ''' Ensure YARA rules are parsed out and their range is returned '''
        async def run():
            peek_rules = self.rules_path.joinpath("peek_rules.yara").resolve()
            rules = peek_rules.read_text()
            pos = protocol.Position(line=42, char=12)
            result = helpers.get_rule_range(rules, pos)
            self.assertIsInstance(result, protocol.Range)
            self.assertEqual(result.start.line, 33)
            self.assertEqual(result.start.char, 0)
            self.assertEqual(result.end.line, 43)
            self.assertEqual(result.end.char, 0)
        self.loop.run_until_complete(run())

    def test_helper_parse_result(self):
        ''' Ensure the parse_result() function properly parses a given diagnostic '''
        result = "line 14: syntax error, unexpected <true>, expecting text string"
        line_no, message = helpers.parse_result(result)
        self.assertEqual(line_no, 14)
        self.assertEqual(message, "syntax error, unexpected <true>, expecting text string")

    def test_helper_parse_result_multicolon(self):
        ''' Sometimes results have colons in the messages - ensure this doesn't affect things '''
        result = "line 15: invalid hex string \"$hex_string\": syntax error"
        line_no, message = helpers.parse_result(result)
        self.assertEqual(line_no, 15)
        self.assertEqual(message, "invalid hex string \"$hex_string\": syntax error")

    def test_helper_parse_uri(self):
        ''' Ensure paths are properly parsed '''
        path = "c:/one/two/three/four.txt"
        file_uri = "file:///{}".format(path)
        self.assertEqual(helpers.parse_uri(file_uri), path)

    def test_helper_resolve_symbol(self):
        ''' Ensure symbols are properly resolved '''
        document = "rule ResolveSymbol {\n strings:\n  $a = \"test\"\n condition:\n  #a > 3\n}\n"
        pos = protocol.Position(line=4, char=3)
        symbol = helpers.resolve_symbol(document, pos)
        self.assertEqual(symbol, "#a")

    #### PROTOCOL.PY TESTS ####
    def test_protocol_diagnostic(self):
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

    def test_protocol_location(self):
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

    def test_protocol_position(self):
        ''' Ensure Position is properly encoded to JSON dictionaries '''
        pos_dict = {"line": 10, "character": 15}
        pos = protocol.Position(line=pos_dict["line"], char=pos_dict["character"])
        self.assertEqual(json.dumps(pos, cls=protocol.JSONEncoder), json.dumps(pos_dict))

    def test_protocol_range(self):
        ''' Ensure Range is properly encoded to JSON dictionaries '''
        pos_dict = {"line": 10, "character": 15}
        pos = protocol.Position(line=pos_dict["line"], char=pos_dict["character"])
        rg_dict = {"start": pos_dict, "end": pos_dict}
        rg = protocol.Range(
            start=pos,
            end=pos
        )
        self.assertEqual(json.dumps(rg, cls=protocol.JSONEncoder), json.dumps(rg_dict))

    #### SERVER.PY TESTS ####
    def test_server_cmd_compile_rule(self):
        ''' Test the "CompileRule" command is successfully executed '''
        self.assertTrue(False)

    def test_server_cmd_compile_all_rules(self):
        ''' Test the "CompileAllRules" command is successfully executed '''
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "workspace/executeCommand",
            "params": {
                "command": "yara.CompileAllRules",
                "arguments": []
            }
        }
        self.assertTrue(False)

    def test_server_code_completion(self):
        ''' Test code completion provider '''
        self.assertTrue(False)

    def test_server_connection_closed(self):
        ''' Ensure the server properly handles closed client connections '''
        self.assertTrue(False)

    def test_server_definitions_rules(self):
        ''' Ensure the definition provider properly resolves any rule names '''
        async def run():
            peek_rules = str(self.rules_path.joinpath("peek_rules.yara").resolve())
            file_uri = helpers.create_file_uri(peek_rules)
            params = {
                "textDocument": {"uri": file_uri},
                "position": {"line": 42, "character": 12}
            }
            result = await self.server.provide_definition(params)
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0], protocol.Location)
            self.assertEqual(result[0].uri, file_uri)
            self.assertEqual(result[0].range.start.line, 5)
            self.assertEqual(result[0].range.start.char, 0)
            self.assertEqual(result[0].range.end.line, 5)
            self.assertEqual(result[0].range.end.char, 18)
        self.loop.run_until_complete(run())

    def test_server_definitions_variables_count(self):
        ''' Ensure the definition provider properly resolves #vars '''
        async def run():
            peek_rules = str(self.rules_path.joinpath("peek_rules.yara").resolve())
            file_uri = helpers.create_file_uri(peek_rules)
            params = {
                "textDocument": {"uri": file_uri},
                "position": {"line": 28, "character": 12}
            }
            result = await self.server.provide_definition(params)
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0], protocol.Location)
            self.assertEqual(result[0].uri, file_uri)
            self.assertEqual(result[0].range.start.line, 21)
            self.assertEqual(result[0].range.start.char, 8)
            self.assertEqual(result[0].range.end.line, 21)
            self.assertEqual(result[0].range.end.char, 19)
        self.loop.run_until_complete(run())

    def test_server_definitions_variables_length(self):
        ''' Ensure the definition provider properly resolves !vars '''
        async def run():
            peek_rules = str(self.rules_path.joinpath("peek_rules.yara").resolve())
            file_uri = helpers.create_file_uri(peek_rules)
            params = {
                "textDocument": {"uri": file_uri},
                "position": {"line": 42, "character": 32}
            }
            result = await self.server.provide_definition(params)
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0], protocol.Location)
            self.assertEqual(result[0].uri, file_uri)
            self.assertEqual(result[0].range.start.line, 40)
            self.assertEqual(result[0].range.start.char, 8)
            self.assertEqual(result[0].range.end.line, 40)
            self.assertEqual(result[0].range.end.char, 22)
        self.loop.run_until_complete(run())

    def test_server_definitions_variables_location(self):
        ''' Ensure the definition provider properly resolves @vars '''
        async def run():
            peek_rules = str(self.rules_path.joinpath("peek_rules.yara").resolve())
            file_uri = helpers.create_file_uri(peek_rules)
            params = {
                "textDocument": {"uri": file_uri},
                "position": {"line": 29, "character": 12}
            }
            result = await self.server.provide_definition(params)
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0], protocol.Location)
            self.assertEqual(result[0].uri, file_uri)
            self.assertEqual(result[0].range.start.line, 21)
            self.assertEqual(result[0].range.start.char, 8)
            self.assertEqual(result[0].range.end.line, 21)
            self.assertEqual(result[0].range.end.char, 19)
        self.loop.run_until_complete(run())

    def test_server_definitions_variables_regular(self):
        ''' Ensure the definition provider properly resolves $vars '''
        async def run():
            peek_rules = str(self.rules_path.joinpath("peek_rules.yara").resolve())
            file_uri = helpers.create_file_uri(peek_rules)
            params = {
                "textDocument": {"uri": file_uri},
                "position": {"line": 24, "character": 12}
            }
            result = await self.server.provide_definition(params)
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0], protocol.Location)
            self.assertEqual(result[0].uri, file_uri)
            self.assertEqual(result[0].range.start.line, 19)
            self.assertEqual(result[0].range.start.char, 8)
            self.assertEqual(result[0].range.end.line, 19)
            self.assertEqual(result[0].range.end.char, 22)
        self.loop.run_until_complete(run())

    def test_server_no_definitions(self):
        ''' Ensure the definition provider does not resolve a non-variable or non-rule '''
        async def run():
            peek_rules = str(self.rules_path.joinpath("peek_rules.yara").resolve())
            file_uri = helpers.create_file_uri(peek_rules)
            params = {
                "textDocument": {"uri": file_uri},
                "position": {"line": 27, "character": 12},
                "context": {"includeDeclaration": True}
            }
            result = await self.server.provide_definition(params)
            self.assertListEqual(result, [])
        self.loop.run_until_complete(run())

    def test_server_diagnostics(self):
        ''' Test diagnostic provider successfully provides '''
        async def run():
            document = "rule OneDiagnostic { condition: $true }"
            result = await self.server.provide_diagnostic(document)
            self.assertEqual(len(result), 1)
            diagnostic = result[0]
            self.assertIsInstance(diagnostic, protocol.Diagnostic)
            self.assertEqual(diagnostic.severity, 1)
            self.assertEqual(diagnostic.message, "undefined string \"$true\"")
            self.assertEqual(diagnostic.range.start.line, 0)
            self.assertEqual(diagnostic.range.end.line, 0)
        self.loop.run_until_complete(run())

    def test_server_no_diagnostics(self):
        ''' Test diagnostic provider does not provide anything '''
        async def run():
            document = "rule NoDiagnostics { condition: true }"
            result = await self.server.provide_diagnostic(document)
            self.assertListEqual(result, [])
        self.loop.run_until_complete(run())

    def test_server_exceptions_handled(self):
        ''' Test the server handles exceptions properly '''
        self.assertTrue(False)

    def test_server_exit(self):
        ''' Test the server exits its process '''
        self.assertTrue(False)

    def test_server_highlights(self):
        ''' Test highlight provider '''
        self.assertTrue(False)

    def test_server_references_rules(self):
        ''' Ensure the reference provider properly resolves any rule names '''
        async def run():
            peek_rules = str(self.rules_path.joinpath("peek_rules.yara").resolve())
            file_uri = helpers.create_file_uri(peek_rules)
            params = {
                "textDocument": {"uri": file_uri},
                "position": {"line": 42, "character": 12},
                "context": {"includeDeclaration": True}
            }
            result = await self.server.provide_reference(params)
            self.assertEqual(len(result), 2)
            for index, location in enumerate(result):
                self.assertIsInstance(location, protocol.Location)
                self.assertEqual(location.uri, file_uri)
                if index == 0:
                    self.assertEqual(location.range.start.line, 5)
                    self.assertEqual(location.range.start.char, 5)
                    self.assertEqual(location.range.end.line, 5)
                    self.assertEqual(location.range.end.char, 18)
                elif index == 1:
                    self.assertEqual(location.range.start.line, 42)
                    self.assertEqual(location.range.start.char, 8)
                    self.assertEqual(location.range.end.line, 42)
                    self.assertEqual(location.range.end.char, 21)
        self.loop.run_until_complete(run())

    def test_server_references_variable(self):
        ''' Ensure the reference provider properly resolves any regular variables '''
        async def run():
            peek_rules = str(self.rules_path.joinpath("peek_rules.yara").resolve())
            file_uri = helpers.create_file_uri(peek_rules)
            params = {
                "textDocument": {"uri": file_uri},
                "position": {"line": 28, "character": 12},
                "context": {"includeDeclaration": True}
            }
            result = await self.server.provide_reference(params)
            self.assertEqual(len(result), 3)
            for index, location in enumerate(result):
                self.assertIsInstance(location, protocol.Location)
                self.assertEqual(location.uri, file_uri)
                if index == 0:
                    self.assertEqual(location.range.start.line, 21)
                    self.assertEqual(location.range.start.char, 8)
                    self.assertEqual(location.range.end.line, 21)
                    self.assertEqual(location.range.end.char, 16)
                elif index == 1:
                    self.assertEqual(location.range.start.line, 28)
                    self.assertEqual(location.range.start.char, 8)
                    self.assertEqual(location.range.end.line, 28)
                    self.assertEqual(location.range.end.char, 16)
                elif index == 2:
                    self.assertEqual(location.range.start.line, 29)
                    self.assertEqual(location.range.start.char, 8)
                    self.assertEqual(location.range.end.line, 29)
                    self.assertEqual(location.range.end.char, 16)
        self.loop.run_until_complete(run())

    def test_server_references_wildcard(self):
        ''' Ensure the reference provider properly resolves wildcard variables '''
        async def run():
            peek_rules = str(self.rules_path.joinpath("peek_rules.yara").resolve())
            file_uri = helpers.create_file_uri(peek_rules)
            params = {
                "textDocument": {"uri": file_uri},
                "position": {"line": 30, "character": 12},
                "context": {"includeDeclaration": True}
            }
            result = await self.server.provide_reference(params)
            self.assertEqual(len(result), 4)
            for index, location in enumerate(result):
                self.assertIsInstance(location, protocol.Location)
                self.assertEqual(location.uri, file_uri)
                if index == 0:
                    self.assertEqual(location.range.start.line, 19)
                    self.assertEqual(location.range.start.char, 8)
                    self.assertEqual(location.range.end.line, 19)
                    self.assertEqual(location.range.end.char, 19)
                elif index == 1:
                    self.assertEqual(location.range.start.line, 20)
                    self.assertEqual(location.range.start.char, 8)
                    self.assertEqual(location.range.end.line, 20)
                    self.assertEqual(location.range.end.char, 20)
                elif index == 2:
                    self.assertEqual(location.range.start.line, 24)
                    self.assertEqual(location.range.start.char, 8)
                    self.assertEqual(location.range.end.line, 24)
                    self.assertEqual(location.range.end.char, 19)
                elif index == 3:
                    self.assertEqual(location.range.start.line, 30)
                    self.assertEqual(location.range.start.char, 8)
                    self.assertEqual(location.range.end.line, 30)
                    self.assertEqual(location.range.end.char, 13)
        self.loop.run_until_complete(run())

    def test_server_renames(self):
        ''' Test rename provider '''
        self.assertTrue(False)

    def test_server_shutdown(self):
        ''' Test the server understands the shutdown message '''
        request = {"jsonrpc":"2.0","id":1,"method":"shutdown","params":None}
        self.assertTrue(False)

    def test_server_single_instance(self):
        ''' Test to make sure there is only a single
        instance of the server when multiple clients connect
        '''
        self.assertTrue(False)

    #### CONNECTION TESTS ####
    def test_transport_closed(self):
        ''' Ensure the transport mechanism is properly closed '''
        async def run():
            try:
                reader, _ = await asyncio.open_connection(self.server_address, self.server_port)
                connection_closed = reader.at_eof()
            except ConnectionRefusedError:
                connection_closed = True
            finally:
                self.assertTrue(connection_closed, "Server connection remains open")
        self.loop.run_until_complete(run())

    def test_transport_opened(self):
        ''' Ensure the transport mechanism is properly opened '''
        async def run():
            try:
                reader, _ = await asyncio.open_connection(self.server_address, self.server_port)
                connection_closed = reader.at_eof()
            except ConnectionRefusedError:
                connection_closed = True
            finally:
                self.assertFalse(connection_closed, "Server connection refused")
        self.loop.run_until_complete(run())


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(YaraLanguageServerTests)
    runner = unittest.TextTestRunner(verbosity=2)
    results = runner.run(suite)
    pct_coverage = ((results.testsRun - (len(results.failures) + len(results.errors))) / results.testsRun) * 100
    print("{:.1f}% test coverage".format(pct_coverage))
