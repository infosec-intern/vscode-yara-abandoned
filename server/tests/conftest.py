""" Reusable test fixtures """
import asyncio
import logging
from pathlib import Path

import pytest


def pytest_configure(config):
    """ Registering custom markers """
    config.addinivalue_line("markers", "config: Run config unittests")
    config.addinivalue_line("markers", "helpers: Run helper function unittests")
    config.addinivalue_line("markers", "protocol: Run language server protocol unittests")
    config.addinivalue_line("markers", "server: Run YARA-specific protocol unittests")
    config.addinivalue_line("markers", "transport: Run network transport unittests")
    config.addinivalue_line("markers", "unix: Tests specific to Unix-based OSes")
    config.addinivalue_line("markers", "windows: Tests specific to the Windows OS")

def noop(x):
    """ No-operation function """
    pass

@pytest.fixture(scope="function")
async def local_server(unused_tcp_port, cb=noop):
    """Set up a local asyncio network server

    :param unused_tcp_port: Random TCP port to bind server to. Provided by pytest-asyncio
    :param cb: Callback function for server to run. Defaults to a no-op function called noop()
    :return: Address and port that server is bound to
    """
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
    logging.debug("Closing server")
    server.close()
    await server.wait_closed()
    logging.debug("Server closed")

@pytest.fixture(scope="function")
def test_rules():
    """ Resolve full path to the test YARA rules """
    rules_path = Path(__file__).parent.joinpath("..", "..", "test", "rules")
    return rules_path.resolve()
