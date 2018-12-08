''' Implements a VSCode language server for YARA '''
import asyncio
import json
import logging
import logging.handlers

try:
    import yara
    HAS_YARA = True
except ModuleNotFoundError:
    logging.warning("yara-python not installed. Diagnostics will not be available")
    HAS_YARA = False

HOST = "127.0.0.1"
LOGGER = logging.getLogger(__name__).addHandler(logging.NullHandler())
PORT = 8471


def _build_logger() -> logging.Logger:
    ''' Build the loggers '''
    global LOGGER
    LOGGER = logging.getLogger(__name__)
    screen_hdlr = logging.StreamHandler()
    screen_hdlr.setFormatter(logging.Formatter("%(message)s"))
    screen_hdlr.setLevel(logging.INFO)
    file_hdlr = logging.handlers.RotatingFileHandler(filename=".yara.log", backupCount=1, maxBytes=100000)
    file_hdlr.setFormatter(logging.Formatter("%(asctime)s | [%(levelname)s:%(module)s:%(lineno)d] %(message)s"))
    file_hdlr.setLevel(logging.DEBUG)
    LOGGER.addHandler(screen_hdlr)
    LOGGER.addHandler(file_hdlr)
    LOGGER.setLevel(logging.DEBUG)

async def code_completion_provider(request: dict) -> str:
    ''' Respond to the completionItem/resolve request '''
    LOGGER.warning("code_completion_provider() is not yet implemented")

async def definition_provider(request: dict) -> str:
    ''' Respond to the textDocument/definition request '''
    LOGGER.warning("definition_provider() is not yet implemented")
    return {
        "jsonrpc": "2.0",
        "id": request["id"],
        "result": {}
    }

async def diagnostic_provider(request: dict) -> str:
    ''' Respond to the textDocument/publishDiagnostics request
    The message carries an array of diagnostic items for a resource URI.
    '''
    if HAS_YARA:
        LOGGER.warning("diagnostic_provider() is not yet implemented")
        logging.debug("yara-python is installed")
        response = {
            "jsonrpc": "2.0",
            "id": request["id"],
            "result": {}
        }
    elif not HAS_YARA:
        LOGGER.error("yara-python is not installed. Diagnostics are disabled")
        response = {}
    return response

async def highlight_provider(request: dict) -> str:
    ''' Respond to the textDocument/documentHighlight request '''
    LOGGER.warning("highlight_provider() is not implemented")
    return {
        "jsonrpc": "2.0",
        "id": request["id"],
        "result": {}
    }

async def reference_provider(request: dict) -> str:
    ''' Respond to the textDocument/references request '''
    LOGGER.warning("reference_provider() is not yet implemented")
    return {
        "jsonrpc": "2.0",
        "id": request["id"],
        "result": {}
    }

async def rename_provider(request: dict) -> str:
    ''' Respond to the textDocument/rename request '''
    LOGGER.warning("rename_provider() is not yet implemented")
    return {
        "jsonrpc": "2.0",
        "id": request["id"],
        "result": {}
    }

async def initialize() -> str:
    ''' Announce language support methods '''
    # document_selector = { "language": "yara", "scheme": "file" }
    LOGGER.debug("inside initialize()")
    return json.dumps({
        "capabilities": {
            # "codeActionProvider": False,
            # "codeLensProvider": False,
            # "colorProvider": False,
            "completionProvider" : {
                "triggerCharacters": [ "." ]
            },
            "definitionProvider": True,
            # "documentFormattingProvider": False,
            "documentHighlightProvider": True,
            # "documentOnTypeFormattingProvider": False,
            # "documentRangeFormattingProvider": False,
            # "documentSymbolProvider": False,
            # "hoverProvider": False,
            "referencesProvider": True,
            "renameProvider": True,
            # "signatureHelpProvider": False,
            # "workspaceSymbolProvider": False,
        }
    }).encode()

async def protocol_handler(reader:asyncio.StreamReader, writer: asyncio.StreamWriter) -> str:
    ''' Handle the language server protocol '''
    announcement = await initialize()
    writer.write(announcement)
    await writer.drain()
    data = await reader.readline()
    key, value = tuple(data.decode().strip().split(" "))
    header = {key: value}
    LOGGER.debug("%s: %s", key, header[key])
    data = await reader.read()
    LOGGER.info(data.decode())
    LOGGER.info("Closing connection")
    writer.close()

async def exception_handler(eventloop: asyncio.BaseEventLoop, context: dict):
    ''' Handle asynchronous exceptions '''
    LOGGER.info("eventloop: %s", eventloop)
    LOGGER.info(type(eventloop))
    LOGGER.info(dir(eventloop))
    LOGGER.info("context: %s", context)
    LOGGER.info(type(context))
    LOGGER.info("message: %s", context["message"])
    LOGGER.info("exception: %s", context["exception"])
    LOGGER.info("future: %s", context["future"])
    LOGGER.info("handle: %s", context["handle"])
    LOGGER.info("protocol: %s", context["protocol"])
    LOGGER.info("transport: %s", context["transport"])
    LOGGER.info("socket: %s", context["socket"])
    eventloop.default_exception_handler(context)

async def main():
    ''' Program entrypoint '''
    _build_logger()
    LOGGER.info("Starting YARA IO language server")
    server = await asyncio.start_server(
        client_connected_cb=protocol_handler,
        host=HOST,
        port=PORT)
    LOGGER.info("Serving on %s", server.sockets[0].getsockname())
    async with server:
        await server.serve_forever()
        LOGGER.info(server.is_serving())
        server.close()

    await server.wait_closed()
    LOGGER.info("server is closed")


if __name__ == "__main__":
    try:
        asyncio.run(main(),debug=True)
    except KeyboardInterrupt:
        LOGGER.critical("Stopping at user's request")
    except Exception as err:
        LOGGER.error("exception thrown")
        LOGGER.exception(err)
