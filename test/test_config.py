import asyncio
from pathlib import Path
import unittest

from .. import helpers, server


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


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(ConfigTests)
    runner = unittest.TextTestRunner(verbosity=2)
    results = runner.run(suite)
    pct_coverage = (results.testsRun - (len(results.failures) + len(results.errors))) / results.testsRun
    print("ConfigTests coverage: {:.1f}%".format(pct_coverage * 100))
