import asyncio
import logging
import socket
import unittest

import languageServer as server


class YaraLanguageServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        ''' Initialize tests '''
        self.yaralangserver = server.YaraLanguageServer()

    @classmethod
    def tearDownClass(self):
        ''' Clean things up '''
        pass

    def test_code_completion_provider(self):
        ''' Test code completion provider '''
        self.assertTrue(False)

    def test_connection_closed(self):
        ''' Ensure the server properly handles closed client connections '''
        self.assertTrue(False)

    def test_definition_provider(self):
        ''' Test defintion provider '''
        self.assertTrue(False)

    def test_diagnostic_provider(self):
        ''' Test diganostic provider '''
        self.assertTrue(False)

    def test_exceptions_handled(self):
        ''' Test the server handles exceptions properly '''
        self.assertTrue(False)

    def test_highlight_provider(self):
        ''' Test highlight provider '''
        self.assertTrue(False)

    def test_reference_provider(self):
        ''' Test reference provider '''
        self.assertTrue(False)

    def test_rename_provider(self):
        ''' Test rename provider '''
        self.assertTrue(False)

    def test_single_instance(self):
        ''' Test to make sure there is only a single
        instance of the server when multiple clients connect
        '''
        self.assertTrue(False)

    def test_transport_kind_opened(self):
        ''' Ensure the transport mechanism is properly opened '''
        try:
            socket.create_connection(("127.0.0.1", 8471))
            connected = True
        except ConnectionRefusedError:
            connected = False
        finally:
            self.assertTrue(connected)

    def test_transport_kind_closed(self):
        ''' Ensure the transport mechanism is properly closed '''
        try:
            socket.create_connection(("127.0.0.1", 8471))
            not_connected = False
        except ConnectionRefusedError:
            not_connected = True
        finally:
            self.assertTrue(not_connected)


if __name__ == "__main__":
    # add all the tet cases to be run
    suite = unittest.TestSuite()
    suite.addTest(YaraLanguageServerTests("test_code_completion_provider"))
    suite.addTest(YaraLanguageServerTests("test_connection_closed"))
    suite.addTest(YaraLanguageServerTests("test_definition_provider"))
    suite.addTest(YaraLanguageServerTests("test_diagnostic_provider"))
    suite.addTest(YaraLanguageServerTests("test_exceptions_handled"))
    suite.addTest(YaraLanguageServerTests("test_highlight_provider"))
    suite.addTest(YaraLanguageServerTests("test_reference_provider"))
    suite.addTest(YaraLanguageServerTests("test_rename_provider"))
    suite.addTest(YaraLanguageServerTests("test_single_instance"))
    suite.addTest(YaraLanguageServerTests("test_transport_kind_opened"))
    suite.addTest(YaraLanguageServerTests("test_transport_kind_closed"))
    # set up a runner and run
    runner = unittest.TextTestRunner(verbosity=2)
    results = runner.run(suite)
    # print results
    pct_coverage = ((results.testsRun - len(results.failures)) / results.testsRun) * 100
    print("{:.1f}% test coverage".format(pct_coverage))
