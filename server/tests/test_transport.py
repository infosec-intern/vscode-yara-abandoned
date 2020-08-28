''' Test the various transport mechanisms used between client and server
    Currently only TCP is supported, though ideally anything supported by
    the asyncio library will be fully integrated and tested in the future
'''
import pytest


@pytest.mark.asyncio
@pytest.mark.transport
async def test_tcp_closed(open_streams):
    ''' Ensure the transport mechanism is properly closed '''
    reader, writer = open_streams
    writer.close()
    await writer.wait_closed()
    assert reader.at_eof() is True

@pytest.mark.asyncio
@pytest.mark.transport
async def test_tcp_opened(open_streams):
    ''' Ensure the transport mechanism is properly opened '''
    reader, writer = open_streams
    assert reader.at_eof() is False
    writer.close()
    await writer.wait_closed()
