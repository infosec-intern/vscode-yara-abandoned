import asyncio
import json
import logging
import socket
import unittest

import helpers
import protocol
import server


class YaraLanguageServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        ''' Initialize tests '''
        self.server = server.YaraLanguageServer()

    @classmethod
    def tearDownClass(self):
        ''' Clean things up '''
        pass

    #### CONFIG TESTS ####
    def test_config_compile_on_save_false(self):
        ''' Ensure documents are not compiled on save when false '''
        self.assertFalse(True)

    def test_config_compile_on_save_true(self):
        ''' Ensure documents are compiled on save when true '''
        self.assertTrue(False)

    def test_config_require_imports_false(self):
        ''' Ensure all code completion suggestions are sent when false '''
        self.assertFalse(True)

    def test_config_require_imports_true(self):
        ''' Ensure only imported modules are suggested when true '''
        self.assertTrue(False)

    #### HELPER.PY TESTS ####
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

    #### PROTOCOL.PY TESTS ####
    def test_protocol_json_encoder(self):
        ''' Ensure objects are properly encoded to JSON dictionaries '''
        pos_dict = {"line": 10, "character": 15}
        pos = protocol.Position(line=pos_dict["line"], char=pos_dict["character"])
        self.assertEqual(json.dumps(pos, cls=protocol.JSONEncoder), json.dumps(pos_dict))
        rg_dict = {"start": pos_dict, "end": pos_dict}
        rg = protocol.Range(
            start=pos,
            end=pos
        )
        self.assertEqual(json.dumps(rg, cls=protocol.JSONEncoder), json.dumps(rg_dict))
        loc = protocol.Location(
            locrange=rg,
            uri="fake:///one/two/three/four.path"
        )
        self.assertEqual(json.dumps(rg, cls=protocol.JSONEncoder), json.dumps(rg_dict))
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

    #### SERVER.PY TESTS ####
    def test_server_code_completion(self):
        ''' Test code completion provider '''
        self.assertTrue(False)

    def test_server_connection_closed(self):
        ''' Ensure the server properly handles closed client connections '''
        self.assertTrue(False)

    def test_server_definitions(self):
        ''' Test defintion provider '''
        self.assertTrue(False)

    def test_server_diagnostics(self):
        ''' Test diagnostic provider successfully provides '''
        self.assertTrue(False)

    def test_server_no_diagnostics(self):
        ''' Test diagnostic provider does not provide anything '''
        # document = "rule NoDiagnostics { condition: true }"
        self.assertTrue(False)

    def test_server_diagnostic_rule_extraction(self):
        '''Ensure the diagnostic provider extracts the rules
        properly and separately
        '''
        self.assertTrue(False)

    def test_server_exceptions_handled(self):
        ''' Test the server handles exceptions properly '''
        self.assertTrue(False)

    def test_server_highlights(self):
        ''' Test highlight provider '''
        self.assertTrue(False)

    def test_server_references(self):
        ''' Test reference provider '''
        self.assertTrue(False)

    def test_server_renames(self):
        ''' Test rename provider '''
        self.assertTrue(False)

    def test_server_single_instance(self):
        ''' Test to make sure there is only a single
        instance of the server when multiple clients connect
        '''
        self.assertTrue(False)

    #### CONNECTION TESTS ####
    def test_transport_closed(self):
        ''' Ensure the transport mechanism is properly closed '''
        try:
            socket.create_connection(("127.0.0.1", 8471))
            not_connected = False
        except ConnectionRefusedError:
            not_connected = True
        finally:
            self.assertTrue(not_connected)

    def test_transport_opened(self):
        ''' Ensure the transport mechanism is properly opened '''
        try:
            socket.create_connection(("127.0.0.1", 8471))
            connected = True
        except ConnectionRefusedError:
            connected = False
        finally:
            self.assertTrue(connected)


if __name__ == "__main__":
    # add all the tet cases to be run
    suite = unittest.TestSuite()
    suite.addTest(YaraLanguageServerTests("test_protocol_json_encoder"))
    suite.addTest(YaraLanguageServerTests("test_helper_parse_result"))
    suite.addTest(YaraLanguageServerTests("test_helper_parse_result_multicolon"))
    suite.addTest(YaraLanguageServerTests("test_helper_parse_uri"))
    suite.addTest(YaraLanguageServerTests("test_transport_closed"))
    suite.addTest(YaraLanguageServerTests("test_transport_opened"))
    # set up a runner and run
    runner = unittest.TextTestRunner(verbosity=2)
    results = runner.run(suite)
    # print results
    pct_coverage = ((results.testsRun - (len(results.failures) + len(results.errors))) / results.testsRun) * 100
    print("{:.1f}% test coverage".format(pct_coverage))
