""" Reusable test fixtures """
import asyncio
import logging
from pathlib import Path

import pytest
from yarals import yarals


def pytest_configure(config):
    """ Registering custom markers """
    config.addinivalue_line("markers", "config: Run config unittests")
    config.addinivalue_line("markers", "helpers: Run helper function unittests")
    config.addinivalue_line("markers", "protocol: Run language server protocol unittests")
    config.addinivalue_line("markers", "server: Run YARA-specific protocol unittests")
    config.addinivalue_line("markers", "transport: Run network transport unittests")


@pytest.fixture(scope="function")
async def local_server(unused_tcp_port):
    """Set up a local asyncio network server

    :param unused_tcp_port: Random TCP port to bind server to. Provided by pytest-asyncio
    :return: Address and port that server is bound to
    """
    def cb(reader, writer):
        """ Non-functional callback """
        pass

    addr = "localhost"
    port = unused_tcp_port
    server = await asyncio.start_server(
        client_connected_cb=cb,
        host=addr,
        port=port,
        start_serving=False
    )
    logging.debug("Returning (%s, %d)", addr, port)
    yield addr, port
    async with server:
        await server.start_serving()
    server.close()
    await server.wait_closed()

@pytest.fixture(scope="function")
def test_rules():
    """ Resolve full path to the test YARA rules """
    rules_path = Path(__file__).parent.joinpath("..", "..", "test", "rules")
    return rules_path.resolve()

@pytest.fixture(scope="function")
def yara_server():
    """ Generate an instance of the YARA language server """
    return yarals.YaraLanguageServer()
