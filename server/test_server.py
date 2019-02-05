import asyncio
import json
import logging
from pathlib import Path
import unittest

import custom_err as ce
import helpers
import protocol
from yarals import YaraLanguageServer


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        ''' Initialize tests '''
        self.rules_path = Path(__file__).parent.joinpath("..", "test", "rules").resolve()
        self.server = YaraLanguageServer()
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
        async def run():
            exit_req = json.dumps({"jsonrpc":"2.0","method":"exit","params":None})
            yarals = YaraLanguageServer()
            with self.assertRaises(ce.ServerExit) as err:
                socket_server = await asyncio.start_server(
                    client_connected_cb=yarals.handle_client,
                    host=self.server_address,
                    port=self.server_port,
                    start_serving=True
                )
                _, writer = await asyncio.open_connection(
                    host=self.server_address,
                    port=self.server_port,
                    loop=socket_server.get_loop()
                )
                await yarals.write_data(exit_req, writer)
                socket_server.close()
                writer.close()
                await socket_server.wait_closed()
                await writer.wait_closed()
            self.assertEqual(str(err), "Server exiting process per client request")
        self.loop.run_until_complete(run())

    @unittest.skip(reason="Still not sure if I want to provide highlights")
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

    def test_no_references(self):
        async def run():
            alienspy = str(self.rules_path.joinpath("apt_alienspy_rat.yar").resolve())
            file_uri = helpers.create_file_uri(alienspy)
            params = {
                "textDocument": {"uri": file_uri},
                "position": {"line": 47, "character": 99},
            }
            document = self.server._get_document(file_uri, dirty_files={})
            result = await self.server.provide_reference(params, document)
            self.assertListEqual(result, [])
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
        async def run():
            shutdown_req = json.dumps({"jsonrpc":"2.0","id":1,"method":"shutdown","params":None})
            yarals = YaraLanguageServer()
            with self.assertLogs(logger=yarals._logger, level=logging.DEBUG) as logs:
                socket_server = await asyncio.start_server(
                    client_connected_cb=yarals.handle_client,
                    host=self.server_address,
                    port=self.server_port,
                    start_serving=True
                )
                _, writer = await asyncio.open_connection(
                    host=self.server_address,
                    port=self.server_port,
                    loop=socket_server.get_loop()
                )
                await yarals.write_data(shutdown_req, writer)
                socket_server.close()
                writer.close()
                await socket_server.wait_closed()
                await writer.wait_closed()
            expected = "INFO:{}:Client has closed".format(yarals._logger.name)
            self.assertIn(expected, logs.output)
        self.loop.run_until_complete(run())

    def test_single_instance(self):
        self.assertTrue(False)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser("Run YaraLanguageServer tests")
    parser.add_argument("-v", dest="verbose", action="count", default=0, help="Change test verbosity")
    args = parser.parse_args()
    if args.verbose > 2:
        args.verbose = 2
    runner = unittest.TextTestRunner(verbosity=args.verbose)
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(ServerTests)
    results = runner.run(suite)
    pct_coverage = (results.testsRun - (len(results.failures) + len(results.errors))) / results.testsRun
    print("ServerTests coverage: {:.1f}%".format(pct_coverage * 100))
