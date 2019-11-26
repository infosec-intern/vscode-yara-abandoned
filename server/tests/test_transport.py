import asyncio
import logging

import pytest


@pytest.mark.asyncio
@pytest.mark.transport
async def test_closed(local_server):
    try:
        srv_addr, srv_port = local_server
        reader, _ = await asyncio.open_connection(srv_addr, srv_port)
        connection_closed = reader.at_eof()
    except ConnectionRefusedError:
        connection_closed = True
    finally:
        assert connection_closed is True, "Server connection remains open"

@pytest.mark.asyncio
@pytest.mark.transport
async def test_opened(local_server):
    ''' Ensure the transport mechanism is properly opened '''
    try:
        srv_addr, srv_port = local_server
        reader, _ = await asyncio.open_connection(srv_addr, srv_port)
        connection_closed = reader.at_eof()
    except ConnectionRefusedError:
        connection_closed = True
    finally:
        connection_closed is False, "Server connection refused"
