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
        self.reader = None
        self.workspace = None
        self.writer = None

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        '''React and respond to client messages

        :reader: asyncio StreamReader. The connected client will write to this stream
        :writer: asyncio.StreamWriter. The connected client will read from this stream
        '''
        current_id = 0
        has_shutdown = False
        has_started = False
        self.reader = reader
        self.writer = writer
        self._logger.info("Client connected")
        while True:
            if self.reader.at_eof():
                self._logger.warning("Client has closed")
                break
            message = await self.read_request()
            if "jsonrpc" in message:
                # this matches some kind of JSON-RPC message
                if "id" in message:
                    # if an id is present, this is a JSON-RPC request
                    current_id = message["id"]
                    if message.get("method", "") == "initialize":
                        self.workspace = urlsplit(unquote(message["params"]["rootUri"], encoding=self._encoding)).path
                        self._logger.info("Client workspace folder: %s", self.workspace)
                        client_options = message.get("params", {}).get("capabilities", {}).get("textDocument", {})
                        announcement = self.initialize(client_options)
                        await self.send_response(curr_id=current_id, response=announcement)
                    elif has_started and message.get("method", "") == "initialized":
                        self._logger.info("Client has been successfully initialized")
                        has_started = True
                    elif has_started and message.get("method", "") == "shutdown":
                        self._logger.info("Client requested shutdown")
                        has_shutdown = True
                        await self.send_response(curr_id=current_id, response={})
                    elif has_started and message.get("method", "") == "exit":
                        self._logger.info("Client requested exit")
                        proper_shutdown = 0 if has_shutdown else 1
                        await self.send_response(curr_id=current_id, response={"success": proper_shutdown})
                        await self.remove_client()
                else:
                    # if no id is present, this is a JSON-RPC notification
                    self._logger.debug("Client sent a notification")
                    self._logger.info(message)
            else:
                # no idea what this message is, let the client know the server is shutting down improperly
                await self.send_error(code=lsp.PARSE_ERROR, curr_id=current_id, msg="Could not parse message")
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
        # we don't want handle_client() to deal with anything other than dicts
        request = {}
        data = await self.reader.readline()
        if data:
            self._logger.debug("header <= %r", data)
            key, value = tuple(data.decode(self._encoding).strip().split(" "))
            header = {key: value}
            self._logger.debug("%s %s", key, header[key])
            # read the extra separator after the initial header
            await self.reader.readuntil(separator=self._eol)
            if key == "Content-Length:":
                data = await self.reader.readexactly(int(value))
            else:
                data = await self.reader.readline()
            self._logger.debug("request <= %r", data)
            request = json.loads(data.decode(self._encoding))
        return request

    async def remove_client(self):
        ''' Close the cient input & output streams '''
        self.writer.close()
        await self.writer.wait_closed()
        self._logger.info("Disconnected client")

    async def send_error(self, code: int, curr_id: int, msg: str):
        ''' Write back a JSON-RPC error message to the client '''
        message = json.dumps({
            "jsonrpc": "2.0",
            "id": curr_id,
            "error": {
                "code": code,
                "message": msg
            }
        }).encode(self._encoding)
        self._logger.debug("error => %s", message)
        self.writer.write(message)
        await self.writer.drain()

    async def send_notification(self, method: str, params: dict):
        ''' Write back a JSON-RPC notification to the client '''
        message = json.dumps({
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }).encode(self._encoding)
        self._logger.debug("notify => %s", message)
        self.writer.write(message)
        await self.writer.drain()

    async def send_response(self, curr_id: int, response: dict):
        ''' Write back a JSON-RPC response to the client '''
        message = json.dumps({
            "jsonrpc": "2.0",
            "id": curr_id,
            "result": response,
        }).replace(" ", "").encode(self._encoding)
        self._logger.debug("response => %r", message)
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
