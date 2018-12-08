import asyncio
import logging
import socket
import unittest

import languageServer as server


class TestLanguageServer(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        ''' Initialize tests '''
        server._build_logger()
        # asyncio.run(server.main())

    @classmethod
    def tearDownClass(self):
        ''' Clean things up '''
        pass

    def test_code_completion_provider(self):
        ''' Test code completion provider '''
        pass

    def test_definition_provider(self):
        ''' Test defintion provider '''
        pass

    def test_diagnostic_provider(self):
        ''' Test diganostic provider '''
        pass

    def test_exceptions_handled(self):
        ''' Test the server handles exceptions properly '''
        pass

    def test_highlight_provider(self):
        ''' Test highlight provider '''
        pass

    def test_reference_provider(self):
        ''' Test reference provider '''
        pass

    def test_rename_provider(self):
        ''' Test rename provider '''
        pass

    def transport_kind_opened(self):
        ''' Ensure the transport mechanism is properly opened '''
        conn = socket.create_connection((server.HOST, server.PORT))
        print(conn)

    def transport_kind_closed(self):
        ''' Ensure the transport mechanism is properly closed '''
        pass

if __name__ == "__main__":
    unittest.main()
