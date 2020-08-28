''' Reusable test fixtures '''
import asyncio
import json
import logging
from pathlib import Path

import pytest
from yarals import yarals


def pytest_configure(config):
    ''' Registering custom markers '''
    config.addinivalue_line("markers", "config: Run config unittests")
    config.addinivalue_line("markers", "helpers: Run helper function unittests")
    config.addinivalue_line("markers", "protocol: Run language server protocol unittests")
    config.addinivalue_line("markers", "server: Run YARA-specific protocol unittests")
    config.addinivalue_line("markers", "transport: Run network transport unittests")

@pytest.fixture(scope="function")
def yara_server():
    ''' Generate an instance of the YARA language server '''
    return yarals.YaraLanguageServer()

@pytest.fixture(scope="function")
async def open_streams(unused_tcp_port, yara_server):
    ''' Set up a local asyncio network server

    :param unused_tcp_port: Random TCP port to bind server to. Provided by pytest-asyncio
    :return: Read/Write streams to interact with server
    '''
    addr = "localhost"
    port = unused_tcp_port
    server = await asyncio.start_server(
        client_connected_cb=yara_server.handle_client,
        host=addr,
        port=port
    )
    await server.start_serving()
    reader, writer = await asyncio.open_connection(addr, port)
    yield reader, writer
    server.close()
    await server.wait_closed()

@pytest.fixture(scope="function")
async def init_server(initialize_msg, initialized_msg):
    ''' Start the given language server with the standard init sequence '''
    async def _init_server(reader, writer, yara_server):
        await yara_server.write_data(initialize_msg, writer)
        await yara_server.read_request(reader)
        await yara_server.write_data(initialized_msg, writer)
        await yara_server.read_request(reader)
    return _init_server

@pytest.fixture(scope="function")
def test_rules():
    ''' Resolve full path to the test YARA rules '''
    rules_path = Path(__file__).parent.joinpath("..", "..", "test", "rules")
    return rules_path.resolve()

@pytest.fixture(scope="module")
def initialize_msg():
    ''' Hardcoded 'initialize' message to start handshake with server '''
    json_path = Path(__file__).parent.joinpath("initialize_msg.json").resolve()
    with json_path.open() as init:
        return json.dumps(json.load(init))

@pytest.fixture(scope="module")
def initialized_msg():
    ''' Hardcoded 'initialized' message to complete client setup with server '''
    return json.dumps({"jsonrpc": "2.0", "method": "initialized", "params": {}})

@pytest.fixture(scope="module")
def shutdown_msg():
    ''' Hardcoded 'initialized' message to complete client setup with server '''
    return json.dumps({"jsonrpc":"2.0","id":1,"method":"shutdown","params":None})

