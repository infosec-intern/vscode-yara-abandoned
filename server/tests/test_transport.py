''' Test the various transport mechanisms used between client and server
    Currently only TCP is supported, though ideally anything supported by
    the asyncio library will be fully integrated and tested in the future
'''
import asyncio
import logging

import pytest


@pytest.mark.asyncio
@pytest.mark.transport
async def test_tcp_closed(local_server):
    srv_addr, srv_port = local_server
    reader, writer = await asyncio.open_connection(srv_addr, srv_port)
    writer.close()
    await writer.wait_closed()
    assert reader.at_eof() is True

@pytest.mark.asyncio
@pytest.mark.transport
async def test_tcp_opened(local_server):
    ''' Ensure the transport mechanism is properly opened '''
    srv_addr, srv_port = local_server
    reader, writer = await asyncio.open_connection(srv_addr, srv_port)
    assert reader.at_eof() is False
    writer.close()
    await writer.wait_closed()
