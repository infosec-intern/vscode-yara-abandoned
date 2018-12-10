import asyncio
import json
import logging
import logging.handlers

from languageServer import YaraLanguageServer

logging.getLogger("yara").addHandler(logging.NullHandler())
LOGGER = logging.getLogger("yara.{}".format(__name__))


def _build_logger() -> logging.Logger:
    ''' Build the loggers '''
    global LOGGER
    LOGGER = logging.getLogger("yara")
    screen_hdlr = logging.StreamHandler()
    screen_hdlr.setFormatter(logging.Formatter("%(message)s"))
    screen_hdlr.setLevel(logging.INFO)
    file_hdlr = logging.handlers.RotatingFileHandler(filename=".yara.log", backupCount=1, maxBytes=100000)
    file_hdlr.setFormatter(logging.Formatter("%(asctime)s | [%(levelname)s:%(module)s:%(lineno)d] %(message)s"))
    file_hdlr.setLevel(logging.DEBUG)
    LOGGER.addHandler(screen_hdlr)
    LOGGER.addHandler(file_hdlr)
    LOGGER.setLevel(logging.DEBUG)

async def main():
    ''' Program entrypoint '''
    _build_logger()
    yaralangserver = YaraLanguageServer()
    LOGGER.info("Starting YARA IO language server")
    socket_server = await asyncio.start_server(
        client_connected_cb=yaralangserver.start,
        host="127.0.0.1",
        port=8471)
    LOGGER.info("Serving on %s", socket_server.sockets[0].getsockname())
    async with socket_server:
        await socket_server.serve_forever()
        LOGGER.info(socket_server.is_serving())
        socket_server.close()
    await socket_server.wait_closed()
    LOGGER.info("server is closed")


if __name__ == "__main__":
    try:
        asyncio.run(main(),debug=True)
    except KeyboardInterrupt:
        LOGGER.critical("Stopping at user's request")
    except Exception as err:
        LOGGER.error("exception thrown")
        LOGGER.exception(err)
