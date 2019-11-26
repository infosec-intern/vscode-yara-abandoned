""" Reusable test fixtures """
import asyncio
import logging

import pytest


def pytest_configure(config):
    """ Registering custom markers """
    config.addinivalue_line("markers", "config: Run config unittests")
    config.addinivalue_line("markers", "helpers: Run helper function unittests")
    config.addinivalue_line("markers", "protocol: Run language server protocol unittests")
    config.addinivalue_line("markers", "server: Run YARA-specific protocol unittests")
    config.addinivalue_line("markers", "transport: Run network transport unittests")

def noop(x):
    """ No-operation function
        Used as a default for network servers
        when no callback is provided
    """
    pass

@pytest.fixture(scope="function")
async def local_server(event_loop, unused_tcp_port, cb=noop):
    """ Set up a local asyncio network server """
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
