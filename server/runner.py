import asyncio
import json
import logging
import logging.handlers

from languageServer import YaraLanguageServer

parent_logger = logging.getLogger("yara")
screen_hdlr = logging.StreamHandler()
screen_hdlr.setFormatter(logging.Formatter("%(name)s | %(message)s"))
screen_hdlr.setLevel(logging.INFO)
file_hdlr = logging.handlers.RotatingFileHandler(filename=".yara.log", backupCount=1, maxBytes=100000)
file_hdlr.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s | %(message)s"))
file_hdlr.setLevel(logging.DEBUG)
parent_logger.addHandler(screen_hdlr)
parent_logger.addHandler(file_hdlr)
parent_logger.setLevel(logging.DEBUG)


async def main():
    ''' Program entrypoint '''
    logger = logging.getLogger("yara.runner")
    yaralangserver = YaraLanguageServer()
    logger.info("Starting YARA IO language server")
    socket_server = await asyncio.start_server(
        client_connected_cb=yaralangserver.handle_client,
        host="127.0.0.1",
        port=8471)
    logger.info("Serving on %s", socket_server.sockets[0].getsockname())
    async with socket_server:
        await socket_server.serve_forever()
        socket_server.close()
    await socket_server.wait_closed()
    LOGGER.info("server is closed")


if __name__ == "__main__":
    try:
        asyncio.run(main(), debug=True)
    except KeyboardInterrupt:
        LOGGER.critical("Stopping at user's request")
    except Exception as err:
        LOGGER.error("exception thrown")
        LOGGER.exception(err)
