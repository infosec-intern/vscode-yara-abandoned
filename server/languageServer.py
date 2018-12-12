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
        self._logger = logging.getLogger("yara.server")
        self._encoding = "utf-8"
        self._eol=b"\r\n"

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        '''React and respond to client messages

        :reader: asyncio StreamReader. The connected client will write to this stream
        :writer: asyncio.StreamWriter. The connected client will read from this stream
        '''
        current_id = 0
        has_shutdown = False
        has_started = False
        workspace = []
        self._logger.info("Client connected")
        while True:
            message = await self.read_request(reader)
            current_id = message["id"]
            if current_id == 0:
                if message["method"] == "initialize":
                    for folder in message["params"]["workspaceFolders"]:
                        workspace.append(urlsplit(unquote(folder["uri"], encoding=self._encoding)).path)
                    announcement = await self.initialize()
                    await self.send_response(announcement, writer)
                    has_started = True
                else: # client is trying to send data before server is initialized
                    error = {
                        "code": lsp.SERVER_NOT_INITIALIZED,
                        "message": "Server has not initialized"
                    }
                    await self.send_response(error, writer)
            elif has_started and message["method"] == "shutdown":
                has_shutdown = True
                await self.send_response({}, writer)
            elif has_started and message["method"] == "exit":
                proper_shutdown = 0 if has_shutdown else 1
                proper_exit = {
                    "success": proper_shutdown
                }
                await self.send_response(proper_exit, writer)
                await self.remove_client(writer)

    async def initialize(self) -> dict:
        ''' Announce language support methods '''
        return {
            "capabilities": {
                "textDocumentSync": lsp.TRANSPORTKIND_FULL
            }
        #     "capabilities": {
        #         "completionProvider" : {
        #             # The server does not provide support to resolve additional information for a completion item
        #             "resolveProvider": False,
        #             "triggerCharacters": ["."]
        #         },
        #         "definitionProvider": True,
        #         "documentFormattingProvider": True,
        #         "documentHighlightProvider": True,
        #         "referencesProvider": True,
        #         "renameProvider": True,
        #         "textDocumentSync": {
        #             # Documents are synced by always sending the full content of the document
        #             "change": 1,
        #             "openClose": False,
        #             # Save notifications are sent to the server
        #             "save": True,
        #             "willSave": False,
        #             "willSaveWaitUntil": False
        #         },
        #         "workspace": {
        #             "workspaceFolders": {
        #                 "changeNotifications": False,
        #                 "supported": False
        #             }
        #         }
        #     }
        }

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
        self._logger.warning("provide_diagnostic() is not yet implemented")
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

    async def read_request(self, reader: asyncio.StreamReader) -> dict:
        ''' Read data from the client '''
        data = await reader.readline()
        key, value = tuple(data.decode(self._encoding).strip().split(" "))
        header = {key: value}
        self._logger.debug("%s %s", key, header[key])
        # read the extra separator after the initial header
        await reader.readuntil(separator=self._eol)
        if key == "Content-Length:":
            data = await reader.readexactly(int(value))
        else:
            data = await reader.readline()
        self._logger.debug("in <= %r", data)
        return json.loads(data.decode(self._encoding))

    async def remove_client(self, writer: asyncio.StreamWriter):
        ''' Close the cient input & output streams '''
        writer.close()
        await writer.wait_closed()
        self._logger.info("Disconnected client")

    async def send_response(self, response: dict, writer: asyncio.StreamWriter):
        ''' Write back to the client '''
        message = json.dumps({
            "result": response
        }).encode(self._encoding)
        self._logger.debug("out => %s", message)
        writer.write(message)
        await writer.drain()
