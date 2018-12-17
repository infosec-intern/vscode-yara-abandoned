''' Implements a VSCode language server for YARA '''
import asyncio
import json
import logging
from urllib.parse import unquote, urlsplit

import protocol as lsp

try:
    import yara
    HAS_YARA = True
except ModuleNotFoundError:
    logging.warning("yara-python not installed. Diagnostics will not be available")
    HAS_YARA = False


class YaraLanguageServer(object):
    def __init__(self):
        ''' Handle the details of the VSCode language server protocol '''
        self._encoding = "utf-8"
        self._eol=b"\r\n"
        self._logger = logging.getLogger("yara")
        self.current_id = 0
        self.reader = None
        self.workspace = None
        self.writer = None

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        '''React and respond to client messages

        :reader: asyncio StreamReader. The connected client will write to this stream
        :writer: asyncio.StreamWriter. The connected client will read from this stream
        '''
        has_shutdown = False
        has_started = False
        self.reader = reader
        self.writer = writer
        self._logger.info("Client connected")
        while True:
            message = await self.read_request()
            self.current_id = message["id"]
            if self.current_id == 0:
                if message["method"] == "initialize":
                    self.workspace = urlsplit(unquote(message["params"]["rootUri"], encoding=self._encoding)).path
                    self._logger.debug("Client workspace folder: %s", self.workspace)
                    client_options = message.get("params", {}).get("capabilities", {}).get("textDocument", {})
                    announcement = self.initialize(client_options)
                    await self.send_response(announcement)
                    has_started = True
                else:
                    # client is trying to send data before server is initialized
                    await self.send_error(code=lsp.SERVER_NOT_INITIALIZED, msg="Server has not initialized")
            elif has_started and message["method"] == "initialized":
                self._logger.debug("Client has been successfully initialized")
            elif has_started and message["method"] == "shutdown":
                self._logger.debug("Client requested shutdown")
                has_shutdown = True
                await self.send_response({})
            elif has_started and message["method"] == "exit":
                self._logger.debug("Client requested exit")
                proper_shutdown = 0 if has_shutdown else 1
                await self.send_response({"success": proper_shutdown})
                await self.remove_client()

    def initialize(self, client_options: dict) -> dict:
        ''' Announce language support methods '''
        server_options = {}
        if client_options.get("synchronization", {}).get("dynamicRegistration", False):
            # Documents are synced by always sending the full content of the document
            server_options["textDocumentSync"] = lsp.TRANSPORTKIND_FULL
        if client_options.get("completion", {}).get("dynamicRegistration", False):
            server_options["completionProvider"] = {
                # The server does not provide support to resolve additional information for a completion item
                "resolveProvider": False,
                "triggerCharacters": ["."]
            }
        if client_options.get("definition", {}).get("dynamicRegistration", False):
            server_options["definitionProvider"] = True
        if client_options.get("references", {}).get("dynamicRegistration", False):
            server_options["referencesProvider"] = True
        if client_options.get("documentHighlight", {}).get("dynamicRegistration", False):
            server_options["documentHighlightProvider"] = True
        if client_options.get("formatting", {}).get("dynamicRegistration", False):
            server_options["documentFormattingProvider"] = True
        if client_options.get("rename", {}).get("dynamicRegistration", False):
            server_options["renameProvider"] = True
        return {"capabilities": server_options}

    async def provide_code_completion(self) -> dict:
        ''' Respond to the completionItem/resolve request '''
        self._logger.warning("provide_code_completion() is not yet implemented")

    async def provide_definition(self) -> dict:
        ''' Respond to the textDocument/definition request '''
        self._logger.warning("provide_definition() is not yet implemented")

    async def provide_diagnostic(self) -> dict:
        ''' Respond to the textDocument/publishDiagnostics request
        The message carries an array of diagnostic items for a resource URI.
        '''
        self._logger.warning("provide_diagnostic() is not et implemented")
        if HAS_YARA:
            logging.debug("yara-python is installed")
        elif not HAS_YARA:
            self._logger.error("yara-python is not installed. Diagnostics are disabled")

    async def provide_highlight(self) -> dict:
        ''' Respond to the textDocument/documentHighlight request '''
        self._logger.warning("provide_highlight() is not implemented")

    async def provide_reference(self) -> dict:
        ''' Respond to the textDocument/references request '''
        self._logger.warning("provide_reference() is not yet implemented")

    async def provide_rename(self) -> dict:
        ''' Respond to the textDocument/rename request '''
        self._logger.warning("provide_rename() is not yet implemented")

    async def read_request(self) -> dict:
        ''' Read data from the client '''
        data = await self.reader.readline()
        self._logger.debug("in <= %r", data)
        key, value = tuple(data.decode(self._encoding).strip().split(" "))
        header = {key: value}
        self._logger.debug("%s %s", key, header[key])
        # read the extra separator after the initial header
        await self.reader.readuntil(separator=self._eol)
        if key == "Content-Length:":
            data = await self.reader.readexactly(int(value))
        else:
            data = await self.reader.readline()
        self._logger.debug("in <= %r", data)
        return json.loads(data.decode(self._encoding))

    async def remove_client(self):
        ''' Close the cient input & output streams '''
        self.writer.close()
        await self.writer.wait_closed()
        self._logger.info("Disconnected client")

    async def send_error(self, code: int, msg: str):
        ''' Write back a JSON-RPC error message to the client '''
        message = json.dumps({
            "jsonrpc": "2.0",
            "id": self.current_id,
            "error": {
                "code": code,
                "message": msg
            }
        }).encode(self._encoding)
        self._logger.debug("error => %s", message)
        self.writer.write(message)
        await self.writer.drain()

    async def send_response(self, response: dict):
        ''' Write back a JSON-RPC response to the client '''
        message = json.dumps({
            "jsonrpc": "2.0",
            "id": self.current_id,
            "result": response,
        }).encode(self._encoding)
        self._logger.debug("out => %s", message)
        self.writer.write(message)
        await self.writer.drain()

    def show_message(self, msg_type: int, msg_text: str) -> dict:
        ''' Ask the client to display a particular message in the user interface '''
        return {
            "method": "window/showMessageRequest",
            "params": {
                "type": msg_type,
                "message": msg_text
            }
        }
