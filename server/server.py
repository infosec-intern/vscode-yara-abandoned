''' Implements a VSCode language server for YARA '''
import asyncio
import json
import logging

import helpers
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
        # variable symbols have a few possible first characters
        self._varchar = ["$", "#", "@", "!"]
        self.num_clients = 0

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        '''React and respond to client messages

        :reader: asyncio StreamReader. The connected client will write to this stream
        :writer: asyncio.StreamWriter. The connected client will read from this stream
        '''
        current_workspace = {"config": None}
        has_shutdown = False
        has_started = False
        self._logger.info("Client connected")
        self.num_clients += 1
        while True:
            if reader.at_eof():
                self._logger.warning("Client has closed")
                self.num_clients -= 1
                break
            message = await self.read_request(reader)
            # this matches some kind of JSON-RPC message
            if "jsonrpc" in message:
                method = message.get("method", "")
                self._logger.info("Client sent a '%s' message", method)
                # if an id is present, this is a JSON-RPC request
                if "id" in message:
                    if not has_started and method == "initialize":
                        self.workspace = helpers.parse_uri(message["params"]["rootUri"], encoding=self._encoding)
                        self._logger.info("Client workspace folder: %s", self.workspace)
                        client_options = message.get("params", {}).get("capabilities", {}).get("textDocument", {})
                        announcement = self.initialize(client_options)
                        await self.send_response(message["id"], announcement, writer)
                    elif has_started and method == "shutdown":
                        self._logger.info("Client requested shutdown")
                        has_shutdown = True
                        await self.send_response(message["id"], {}, writer)
                    elif has_started and method == "textDocument/completion":
                        completions = await self.provide_code_completion(message["params"])
                        await self.send_response(message["id"], completions, writer)
                    elif has_started and method == "textDocument/definition":
                        definition = await self.provide_definition(message["params"])
                        await self.send_response(message["id"], definition, writer)
                    elif has_started and method == "textDocument/documentHighlight":
                        highlights = await self.provide_highlight(message["params"])
                        await self.send_response(message["id"], highlights, writer)
                    elif has_started and method == "textDocument/references":
                        references = await self.provide_reference(message["params"])
                        await self.send_response(message["id"], references, writer)
                    elif has_started and method == "textDocument/rename":
                        renames = await self.provide_rename(message["params"])
                        await self.send_response(message["id"], renames, writer)
                # if no id is present, this is a JSON-RPC notification
                else:
                    if method == "initialized":
                        self._logger.info("Client has been successfully initialized")
                        has_started = True
                        params = {"type": lsp.MessageType.INFO, "message": "Successfully connected"}
                        await self.send_notification("window/showMessageRequest", params, writer)
                    elif has_started and method == "exit":
                        self._logger.info("Client requested exit")
                        proper_shutdown = 0 if has_shutdown else 1
                        await self.send_response(None, {"success": proper_shutdown}, writer)
                        await self.remove_client(writer)
                    elif has_started and method == "workspace/didChangeConfiguration":
                        current_workspace["config"] = message.get("params", {}).get("settings", {}).get("yara", {})
                        self._logger.debug("Changed workspace config to %s", json.dumps(current_workspace["config"]))
                        if current_workspace["config"].get("trace", {}).get("server", "off") == "on":
                            # TODO: add another logging handler to output DEBUG logs to VSCode's channel
                            self._logger.info("Ignoring trace request for now")
                    elif has_started and method == "textDocument/didSave":
                        file_uri = message.get("params", {}).get("textDocument", {}).get("uri", "")
                        file_path = helpers.parse_uri(file_uri)
                        with open(file_path, "rb") as ifile:
                            document = ifile.read().decode(self._encoding)
                            diagnostics = await self.provide_diagnostic(document)
                            params = {
                                "uri": file_uri,
                                "diagnostics": diagnostics
                            }
                            await self.send_notification("textDocument/publishDiagnostics", params, writer)

    def initialize(self, client_options: dict) -> dict:
        '''Announce language support methods

        :client_options: Dictionary of registration options that the client supports
        '''
        server_options = {}
        if client_options.get("synchronization", {}).get("dynamicRegistration", False):
            # Documents are synced by always sending the full content of the document
            server_options["textDocumentSync"] = lsp.TextSyncKind.FULL
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
        # if client_options.get("documentHighlight", {}).get("dynamicRegistration", False):
        #     server_options["documentHighlightProvider"] = True
        if client_options.get("formatting", {}).get("dynamicRegistration", False):
            server_options["documentFormattingProvider"] = True
        if client_options.get("rename", {}).get("dynamicRegistration", False):
            server_options["renameProvider"] = True
        return {"capabilities": server_options}

    async def provide_code_completion(self, params: dict) -> dict:
        '''Respond to the completionItem/resolve request

        :params:
        '''
        self._logger.warning("provide_code_completion() is not yet implemented")
        symbol_pos = lsp.Position(line=params["position"]["line"], char=params["position"]["character"])
        completion_context = lsp.CompletionTriggerKind(params["context"]["triggerKind"])
        return {}

    async def provide_definition(self, params: dict) -> dict:
        ''' Respond to the textDocument/definition request '''
        self._logger.warning("provide_definition() is not yet implemented")
        return {}

    async def provide_diagnostic(self, text_document: str) -> dict:
        ''' Respond to the textDocument/publishDiagnostics request

        :text_document: Contents of YARA rule file
        '''
        if HAS_YARA:
            self._logger.warning("provide_diagnostic() is not yet implemented")
            diagnostics = []
            rules = []
            # 1. identify where each rule starts and ends
            lines = text_document.split("\n")
            for index in range(0, len(lines)):
                if "condition:" in lines[index]:
                    # exact character doesn't actually matter here, just the line number
                    rule_range = helpers.get_rule_range(text_document, lsp.Position(index, 0))
                    rule = "\n".join(lines[rule_range.start.line:rule_range.end.line])
                    # subtract 1 here because line 1 == offset 0
                    rules.append((rule, rule_range.start.line-1))
            # 2. compile each rule individually
            for rule, offset in rules:
                try:
                    yara.compile(source=rule)
                # 3. parse results
                except yara.SyntaxError as error:
                    line_no, msg = helpers.parse_result(str(error))
                    symbol_range = lsp.Range(
                        start=lsp.Position(offset+line_no, 0),
                        end=lsp.Position(offset+line_no, 10000)
                    )
                    diagnostics.append(
                        lsp.Diagnostic(
                            locrange=symbol_range,
                            severity=lsp.DiagnosticSeverity.ERROR,
                            code=0,
                            message=msg
                        )
                    )
                except yara.WarningError as warning:
                    line_no, msg = helpers.parse_result(str(warning))
                    symbol_range = lsp.Range(
                        start=lsp.Position(offset+line_no, 0),
                        end=lsp.Position(offset+line_no, 10000)
                    )
                    diagnostics.append(
                        lsp.Diagnostic(
                            locrange=symbol_range,
                            severity=lsp.DiagnosticSeverity.WARNING,
                            code=1,
                            message=msg
                        )
                    )
            return diagnostics
        else:
            self._logger.error("yara-python is not installed. Diagnostics are disabled")
            return []

    async def provide_highlight(self, params: dict) -> dict:
        ''' Respond to the textDocument/documentHighlight request '''
        self._logger.warning("provide_highlight() is not implemented")
        return {}

    async def provide_reference(self, params: dict) -> dict:
        ''' Respond to the textDocument/references request '''
        self._logger.warning("provide_reference() is not yet implemented")
        return {}

    async def provide_rename(self, params: dict) -> dict:
        ''' Respond to the textDocument/rename request '''
        self._logger.warning("provide_rename() is not yet implemented")
        new_symbol_name = params["newName"]
        symbol_pos = lsp.Position(line=params["position"]["line"], char=params["position"]["character"])
        curr_symbol_name = helpers.resolve_symbol(params["textDocument"], symbol_pos)
        # it's possible the user tries to rename a non-symbol
        if curr_symbol_name is None:
            return {}
        else:
            rule_range = helpers.get_rule(params["textDocument"], symbol_pos)
            return {}

    async def read_request(self, reader: asyncio.StreamReader) -> dict:
        ''' Read data from the client '''
        # we don't want handle_client() to deal with anything other than dicts
        request = {}
        data = await reader.readline()
        if data:
            # self._logger.debug("header <= %r", data)
            key, value = tuple(data.decode(self._encoding).strip().split(" "))
            # read the extra separator after the initial header
            await reader.readuntil(separator=self._eol)
            if key == "Content-Length:":
                data = await reader.readexactly(int(value))
            else:
                data = await reader.readline()
            # self._logger.debug("input <= %r", data)
            request = json.loads(data.decode(self._encoding))
        return request

    async def remove_client(self, writer: asyncio.StreamWriter):
        ''' Close the cient input & output streams '''
        if writer.can_write_eof():
            writer.write_eof()
        writer.close()
        await writer.wait_closed()
        self._logger.info("Disconnected client")

    async def send_error(self, code: int, curr_id: int, msg: str, writer: asyncio.StreamWriter):
        ''' Write back a JSON-RPC error message to the client '''
        message = json.dumps({
            "jsonrpc": "2.0",
            "id": curr_id,
            "error": {
                "code": code,
                "message": msg
            }
        }, cls=lsp.JSONEncoder)
        await self.write_data(message, writer)

    async def send_notification(self, method: str, params: dict, writer: asyncio.StreamWriter):
        ''' Write back a JSON-RPC notification to the client '''
        message = json.dumps({
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }, cls=lsp.JSONEncoder)
        await self.write_data(message, writer)

    async def send_response(self, curr_id: int, response: dict, writer: asyncio.StreamWriter):
        ''' Write back a JSON-RPC response to the client '''
        message = json.dumps({
            "jsonrpc": "2.0",
            "id": curr_id,
            "result": response,
        }, cls=lsp.JSONEncoder)
        await self.write_data(message, writer)

    async def write_data(self, message: str, writer: asyncio.StreamWriter):
        ''' Write a JSON-RPC message to the given stream with the proper encoding and formatting '''
        # self._logger.debug("output => %r", message.encode(self._encoding))
        writer.write("Content-Length: {:d}\r\n\r\n{:s}".format(len(message), message).encode(self._encoding))
        await writer.drain()
