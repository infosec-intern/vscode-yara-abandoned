import asyncio
import unittest

from yarals.yarals import YaraLanguageServer


class TransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        ''' Initialize tests '''
        self.server_address = "127.0.0.1"
        self.server_port = 8471
        self.yarals = YaraLanguageServer()

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


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser("Run server transport tests")
    parser.add_argument("-v", dest="verbose", action="count", default=0, help="Change test verbosity")
    args = parser.parse_args()
    if args.verbose > 2:
        args.verbose = 2
    runner = unittest.TextTestRunner(verbosity=args.verbose)
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TransportTests)
    results = runner.run(suite)
    pct_coverage = (results.testsRun - (len(results.failures) + len(results.errors))) / results.testsRun
    print("TransportTests coverage: {:.1f}%".format(pct_coverage * 100))
