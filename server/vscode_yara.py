#!/usr/bin/env python3

import asyncio
import json
import logging
import logging.handlers

from yarals.yarals import YaraLanguageServer

logger = logging.getLogger("yara")
screen_hdlr = logging.StreamHandler()
screen_hdlr.setFormatter(logging.Formatter("%(name)s.%(module)s | %(message)s"))
screen_hdlr.setLevel(logging.INFO)
file_hdlr = logging.handlers.RotatingFileHandler(filename=".yara.log", backupCount=1, maxBytes=100000)
file_hdlr.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s | %(message)s"))
file_hdlr.setLevel(logging.DEBUG)
logger.addHandler(screen_hdlr)
logger.addHandler(file_hdlr)
logger.setLevel(logging.DEBUG)


async def main():
    ''' Program entrypoint '''
    yarals = YaraLanguageServer()
    logger.info("Starting YARA IO language server")
    socket_server = await asyncio.start_server(
        client_connected_cb=yarals.handle_client,
        host="127.0.0.1",
        port=8471,
        start_serving=False
    )
    servhost, servport = socket_server.sockets[0].getsockname()
    logger.info("Serving on tcp://%s:%d", servhost, servport)
    try:
        async with socket_server:
            await socket_server.serve_forever()
    except asyncio.CancelledError:
        logger.info("Server has successfully shutdown")


asyncio.run(main(), debug=True)
