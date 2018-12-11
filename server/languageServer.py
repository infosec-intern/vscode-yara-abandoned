''' Implements a VSCode language server for YARA '''
import asyncio
import json
import logging

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
        self._separator=b"\r\n"
        self.input = None
        self.output = None

    async def handler(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        '''React and respond to client messages

        :reader: asyncio StreamReader. The connected client will write to this stream
        :writer: asyncio.StreamWriter. The connected client will read from this stream
        '''
        self._logger.info("Client connected")
        self.input = reader
        self.output = writer
        try:
            while True:
                message = await self.read_request()
                if message["method"] == "initialize":
                    announcement = await self.initialize()
                    await self.send_response(announcement)
                    self._logger.debug("response sent")
        except KeyboardInterrupt:
            self._logger.error("Closing handler()")

    async def initialize(self) -> dict:
        ''' Announce language support methods '''
        return {
            "capabilities": {
                "completionProvider" : {
                    "triggerCharacters": [ "." ]
                },
                "definitionProvider": True,
                "documentHighlightProvider": True,
                "referencesProvider": True,
                "renameProvider": True
            }
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

    async def read_request(self) -> dict:
        ''' Read data from the client '''
        data = await self.input.readuntil(separator=self._separator)
        key, value = tuple(data.decode().strip().split(" "))
        header = {key: value}
        self._logger.debug("%s %s", key, header[key])
        # read the extra line after the initial header
        await self.input.readuntil(separator=self._separator)
        if key == "Content-Length:":
            data = await self.input.readexactly(int(value))
        else:
            data = await self.input.readuntil(separator=self._separator)
        self._logger.debug("in <= %r", data)
        return json.loads(data.decode())

    async def send_response(self, message: dict):
        ''' Write back to the client '''
        self._logger.debug("out => %s", message)
        self.output.write(json.dumps(message).encode("utf-8"))
        await self.output.drain()
