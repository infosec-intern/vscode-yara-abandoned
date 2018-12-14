import asyncio
import json
import logging
import logging.handlers

from server import YaraLanguageServer

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


def exc_handler(loop, context: dict):
    ''' Appropriately handle exceptions '''
    future = context["future"]
    try:
        server = future.result()
        print("future result: %s" % server)
    except ConnectionResetError:
        logger.error("Client disconnected unexpectedly")
        loop.stop()
        logger.info("Server is closed")
    except Exception as err:
        logger.critical("Unknown exception encountered")
        logger.critical(err)
        loop.stop()
        logger.info("Server is closed")

async def main():
    ''' Program entrypoint '''
    yaralangserver = YaraLanguageServer()
    logger.info("Starting YARA IO language server")
    socket_server = await asyncio.start_server(
        client_connected_cb=yaralangserver.handle_client,
        host="127.0.0.1",
        port=8471)
    socket_server.get_loop().set_exception_handler(exc_handler)
    servhost, servport = socket_server.sockets[0].getsockname()
    logger.info("Serving on tcp://%s:%d", servhost, servport)
    async with socket_server:
        await socket_server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main(), debug=True)
    except Exception as err:
        logging.exception(err)

