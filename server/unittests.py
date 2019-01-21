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


class ConfigTests(unittest.TestCase):
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

    def test_compile_on_save_false(self):
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

    def test_compile_on_save_true(self):
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

class HelperTests(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        ''' Initialize tests '''
        self.rules_path = Path(__file__).parent.joinpath("..", "test", "rules").resolve()

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

class ProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        pass

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

class ServerTests(unittest.TestCase):
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

    def test_cmd_compile_rule(self):
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "workspace/executeCommand",
            "params": {
                "command": "yara.CompileRule",
                "arguments": []
            }
        }
        self.assertTrue(False)

    def test_cmd_compile_all_rules(self):
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

    def test_code_completion_regular(self):
        async def run():
            actual = []
            code_completion = str(self.rules_path.joinpath("code_completion.yara").resolve())
            expected = ["network", "registry", "filesystem", "sync"]
            file_uri = helpers.create_file_uri(code_completion)
            params = {
                "textDocument": {"uri": file_uri},
                "position": {"line": 9, "character": 15}
            }
            document = self.server._get_document(file_uri, dirty_files={})
            result = await self.server.provide_code_completion(params, document)
            self.assertEqual(len(result), 4)
            for completion in result:
                self.assertIsInstance(completion, protocol.CompletionItem)
                actual.append(completion.label)
            self.assertListEqual(actual, expected)
        self.loop.run_until_complete(run())

    def test_code_completion_overflow(self):
        async def run():
            code_completion = str(self.rules_path.joinpath("code_completion.yara").resolve())
            file_uri = helpers.create_file_uri(code_completion)
            params = {
                "textDocument": {"uri": file_uri},
                "position": {"line": 9, "character": 25}
            }
            document = self.server._get_document(file_uri, dirty_files={})
            result = await self.server.provide_code_completion(params, document)
            self.assertListEqual(result, [])
        self.loop.run_until_complete(run())

    def test_code_completion_unexpected(self):
        async def run():
            code_completion = str(self.rules_path.joinpath("code_completion.yara").resolve())
            file_uri = helpers.create_file_uri(code_completion)
            params = {
                "textDocument": {"uri": file_uri},
                "position": {"line": 8, "character": 25}
            }
            document = self.server._get_document(file_uri, dirty_files={})
            result = await self.server.provide_code_completion(params, document)
            self.assertListEqual(result, [])
        self.loop.run_until_complete(run())

    def test_definitions_rules(self):
        async def run():
            peek_rules = str(self.rules_path.joinpath("peek_rules.yara").resolve())
            file_uri = helpers.create_file_uri(peek_rules)
            params = {
                "textDocument": {"uri": file_uri},
                "position": {"line": 42, "character": 12}
            }
            document = self.server._get_document(file_uri, dirty_files={})
            result = await self.server.provide_definition(params, document)
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0], protocol.Location)
            self.assertEqual(result[0].uri, file_uri)
            self.assertEqual(result[0].range.start.line, 5)
            self.assertEqual(result[0].range.start.char, 0)
            self.assertEqual(result[0].range.end.line, 5)
            self.assertEqual(result[0].range.end.char, 18)
        self.loop.run_until_complete(run())

    def test_definitions_variables_count(self):
        async def run():
            peek_rules = str(self.rules_path.joinpath("peek_rules.yara").resolve())
            file_uri = helpers.create_file_uri(peek_rules)
            params = {
                "textDocument": {"uri": file_uri},
                "position": {"line": 28, "character": 12}
            }
            document = self.server._get_document(file_uri, dirty_files={})
            result = await self.server.provide_definition(params, document)
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0], protocol.Location)
            self.assertEqual(result[0].uri, file_uri)
            self.assertEqual(result[0].range.start.line, 21)
            self.assertEqual(result[0].range.start.char, 8)
            self.assertEqual(result[0].range.end.line, 21)
            self.assertEqual(result[0].range.end.char, 19)
        self.loop.run_until_complete(run())

    def test_definitions_variables_length(self):
        async def run():
            peek_rules = str(self.rules_path.joinpath("peek_rules.yara").resolve())
            file_uri = helpers.create_file_uri(peek_rules)
            params = {
                "textDocument": {"uri": file_uri},
                "position": {"line": 42, "character": 32}
            }
            document = self.server._get_document(file_uri, dirty_files={})
            result = await self.server.provide_definition(params, document)
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0], protocol.Location)
            self.assertEqual(result[0].uri, file_uri)
            self.assertEqual(result[0].range.start.line, 40)
            self.assertEqual(result[0].range.start.char, 8)
            self.assertEqual(result[0].range.end.line, 40)
            self.assertEqual(result[0].range.end.char, 22)
        self.loop.run_until_complete(run())

    def test_definitions_variables_location(self):
        async def run():
            peek_rules = str(self.rules_path.joinpath("peek_rules.yara").resolve())
            file_uri = helpers.create_file_uri(peek_rules)
            params = {
                "textDocument": {"uri": file_uri},
                "position": {"line": 29, "character": 12}
            }
            document = self.server._get_document(file_uri, dirty_files={})
            result = await self.server.provide_definition(params, document)
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0], protocol.Location)
            self.assertEqual(result[0].uri, file_uri)
            self.assertEqual(result[0].range.start.line, 21)
            self.assertEqual(result[0].range.start.char, 8)
            self.assertEqual(result[0].range.end.line, 21)
            self.assertEqual(result[0].range.end.char, 19)
        self.loop.run_until_complete(run())

    def test_definitions_variables_regular(self):
        async def run():
            peek_rules = str(self.rules_path.joinpath("peek_rules.yara").resolve())
            file_uri = helpers.create_file_uri(peek_rules)
            params = {
                "textDocument": {"uri": file_uri},
                "position": {"line": 24, "character": 12}
            }
            document = self.server._get_document(file_uri, dirty_files={})
            result = await self.server.provide_definition(params, document)
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0], protocol.Location)
            self.assertEqual(result[0].uri, file_uri)
            self.assertEqual(result[0].range.start.line, 19)
            self.assertEqual(result[0].range.start.char, 8)
            self.assertEqual(result[0].range.end.line, 19)
            self.assertEqual(result[0].range.end.char, 22)
        self.loop.run_until_complete(run())

    def test_no_definitions(self):
        async def run():
            peek_rules = str(self.rules_path.joinpath("peek_rules.yara").resolve())
            file_uri = helpers.create_file_uri(peek_rules)
            params = {
                "textDocument": {"uri": file_uri},
                "position": {"line": 27, "character": 12},
                "context": {"includeDeclaration": True}
            }
            document = self.server._get_document(file_uri, dirty_files={})
            result = await self.server.provide_definition(params, document)
            self.assertListEqual(result, [])
        self.loop.run_until_complete(run())

    def test_diagnostics(self):
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

    def test_no_diagnostics(self):
        async def run():
            document = "rule NoDiagnostics { condition: true }"
            result = await self.server.provide_diagnostic(document)
            self.assertListEqual(result, [])
        self.loop.run_until_complete(run())

    def test_dirty_files(self):
        peek_rules = str(self.rules_path.joinpath("peek_rules.yara").resolve())
        file_uri = helpers.create_file_uri(peek_rules)
        unsaved_changes = "rule ResolveSymbol {\n strings:\n  $a = \"test\"\n condition:\n  #a > 3\n}\n"
        dirty_files = {
            file_uri: unsaved_changes
        }
        document = self.server._get_document(file_uri, dirty_files)
        self.assertEqual(document, unsaved_changes)

    def test_exceptions_handled(self):
        self.assertTrue(False)

    def test_exit(self):
        request = {
            "jsonrpc": "2.0",
            "method": "exit",
            "params": {}
        }
        self.assertTrue(False)

    def test_highlights(self):
        self.assertTrue(False)

    def test_hover(self):
        async def run():
            peek_rules = str(self.rules_path.joinpath("peek_rules.yara").resolve())
            file_uri = helpers.create_file_uri(peek_rules)
            params = {
                "textDocument": {"uri": file_uri},
                "position": {"line": 29, "character": 12}
            }
            document = self.server._get_document(file_uri, dirty_files={})
            result = await self.server.provide_hover(params, document)
            self.assertIsInstance(result, protocol.Hover)
            self.assertEqual(result.contents.kind, protocol.MarkupKind.Plaintext)
            self.assertEqual(result.contents.value, "\"double string\" wide nocase fullword")
        self.loop.run_until_complete(run())

    def test_no_hover(self):
        async def run():
            peek_rules = str(self.rules_path.joinpath("peek_rules.yara").resolve())
            file_uri = helpers.create_file_uri(peek_rules)
            params = {
                "textDocument": {"uri": file_uri},
                "position": {"line": 25, "character": 12}
            }
            document = self.server._get_document(file_uri, dirty_files={})
            result = await self.server.provide_hover(params, document)
            self.assertIs(result, None)
        self.loop.run_until_complete(run())

    def test_references_rules(self):
        async def run():
            peek_rules = str(self.rules_path.joinpath("peek_rules.yara").resolve())
            file_uri = helpers.create_file_uri(peek_rules)
            params = {
                "textDocument": {"uri": file_uri},
                "position": {"line": 42, "character": 12},
                "context": {"includeDeclaration": True}
            }
            document = self.server._get_document(file_uri, dirty_files={})
            result = await self.server.provide_reference(params, document)
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

    def test_references_variable(self):
        async def run():
            peek_rules = str(self.rules_path.joinpath("peek_rules.yara").resolve())
            file_uri = helpers.create_file_uri(peek_rules)
            params = {
                "textDocument": {"uri": file_uri},
                "position": {"line": 28, "character": 12},
                "context": {"includeDeclaration": True}
            }
            document = self.server._get_document(file_uri, dirty_files={})
            result = await self.server.provide_reference(params, document)
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

    def test_references_wildcard(self):
        async def run():
            peek_rules = str(self.rules_path.joinpath("peek_rules.yara").resolve())
            file_uri = helpers.create_file_uri(peek_rules)
            params = {
                "textDocument": {"uri": file_uri},
                "position": {"line": 30, "character": 12},
                "context": {"includeDeclaration": True}
            }
            document = self.server._get_document(file_uri, dirty_files={})
            result = await self.server.provide_reference(params, document)
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

    @unittest.skip(reason="Still not sure if I want to provide renames")
    def test_renames(self):
        async def run():
            peek_rules = str(self.rules_path.joinpath("peek_rules.yara").resolve())
            file_uri = helpers.create_file_uri(peek_rules)
            params = {
                "textDocument": {"uri": file_uri},
                "position": {"line": 29, "character": 12},
                "newName": "test_rename"
            }
            document = self.server._get_document(file_uri, dirty_files={})
            result = await self.server.provide_rename(params, document)
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0], protocol.WorkspaceEdit)
        self.loop.run_until_complete(run())

    def test_shutdown(self):
        request = {"jsonrpc":"2.0","id":1,"method":"shutdown","params":None}
        self.assertTrue(False)

    def test_single_instance(self):
        self.assertTrue(False)

class TransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        ''' Initialize tests '''
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

    def test_closed(self):
        async def run():
            try:
                reader, _ = await asyncio.open_connection(self.server_address, self.server_port)
                connection_closed = reader.at_eof()
            except ConnectionRefusedError:
                connection_closed = True
            finally:
                self.assertTrue(connection_closed, "Server connection remains open")
        self.loop.run_until_complete(run())

    def test_opened(self):
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

def run_test_suite(name: str, testcase: unittest.TestCase):
    ''' Run a test suite and display results with the given name'''
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(testcase)
    runner = unittest.TextTestRunner(verbosity=2)
    results = runner.run(suite)
    pct_coverage = (results.testsRun - (len(results.failures) + len(results.errors))) / results.testsRun
    print("{} test coverage: {:.1f}%".format(name.capitalize(), pct_coverage * 100))
    return pct_coverage


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--all", action="store_true", help="Run all tests")
    parser.add_argument("-c", "--config", action="store_true", help="Run config tests")
    parser.add_argument("-e", "--helper", action="store_true", help="Run helper tests")
    parser.add_argument("-p", "--protocol", action="store_true", help="Run protocol tests")
    parser.add_argument("-s", "--server", action="store_true", help="Run server tests")
    parser.add_argument("-t", "--transport", action="store_true", help="Run transport tests")
    args = parser.parse_args()

    total_coverage = []
    if args.all or args.config:
        total_coverage.append(run_test_suite("config", ConfigTests))
    if args.all or args.helper:
        total_coverage.append(run_test_suite("helper", HelperTests))
    if args.all or args.protocol:
        total_coverage.append(run_test_suite("protocol", ProtocolTests))
    if args.all or args.server:
        total_coverage.append(run_test_suite("server", ServerTests))
    if args.all or args.transport:
        total_coverage.append(run_test_suite("transport", TransportTests))
    if not (args.all or args.config or args.helper or args.protocol or args.server or args.transport):
        parser.print_help()

    if len(total_coverage) > 1:
        print("\nTotal test coverage: {:.1f}%".format((sum(total_coverage) / len(total_coverage)) * 100))
