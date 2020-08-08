""" Reusable test fixtures """
import asyncio
import json
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
def yara_server():
    """ Generate an instance of the YARA language server """
    return yarals.YaraLanguageServer()

@pytest.fixture(scope="function")
async def local_server(unused_tcp_port, yara_server):
    """Set up a local asyncio network server

    :param unused_tcp_port: Random TCP port to bind server to. Provided by pytest-asyncio
    :return: Address and port that server is bound to
    """
    addr = "localhost"
    port = unused_tcp_port
    server = await asyncio.start_server(
        client_connected_cb=yara_server.handle_client,
        host=addr,
        port=port,
        start_serving=True
    )
    yield addr, port
    server.close()
    await server.wait_closed()

@pytest.fixture(scope="function")
def test_rules():
    """ Resolve full path to the test YARA rules """
    rules_path = Path(__file__).parent.joinpath("..", "..", "test", "rules")
    return rules_path.resolve()

@pytest.fixture(scope="module")
def initialize_msg():
    """ Hardcoded 'initialize' message to start handshake with server """
    json_path = Path(__file__).parent.joinpath("initialize_msg.json").resolve()
    with json_path.open() as init:
        return json.dumps(json.load(init))

@pytest.fixture(scope="module")
def initialized_msg():
    """ Hardcoded 'initialized' message to complete client setup with server """
    return json.dumps({"jsonrpc": "2.0", "method": "initialized", "params": {}})

@pytest.fixture(scope="module")
def shutdown_msg():
    """ Hardcoded 'initialized' message to complete client setup with server """
    return json.dumps({"jsonrpc":"2.0","id":1,"method":"shutdown","params":None})

