''' Implements a VSCode language server for YARA '''
import asyncio
import json
import logging
from pathlib import Path
import re

import custom_err as ce
import helpers
import protocol as lsp

try:
    import yara
    HAS_YARA = True
except ModuleNotFoundError:
    HAS_YARA = False
    # cannot notify user at this point unfortunately - no clients have connected
    logging.warning("yara-python is not installed. Diagnostics and Compile commands are disabled")


class YaraLanguageServer(object):
    def __init__(self):
        ''' Handle the details of the VSCode language server protocol '''
        self._encoding = "utf-8"
        self._eol=b"\r\n"
        self._logger = logging.getLogger("yara")
        # variable symbols have a few possible first characters
        self._varchar = ["$", "#", "@", "!"]
        self.diagnostics_warned = False
        self.hover_langs = [lsp.MarkupKind.Markdown, lsp.MarkupKind.Plaintext]
        self.num_clients = 0
        schema = Path(__file__).parent.joinpath("modules.json").resolve()
        self.modules = json.loads(schema.read_text())

    def _get_document(self, file_uri: str, dirty_files: dict) -> str:
        ''' Return the document text for a given file URI either from disk or memory '''
        if file_uri in dirty_files:
            return dirty_files[file_uri]
        file_path = helpers.parse_uri(file_uri, encoding=self._encoding)
        with open(file_path, "r") as rule_file:
            return rule_file.read()

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        '''React and respond to client messages

        :reader: asyncio StreamReader. The connected client will write to this stream
        :writer: asyncio.StreamWriter. The connected client will read from this stream
        '''
        config = {}
        # file_uri => contents
        dirty_files = {}
        has_started = False
        self._logger.info("Client connected")
        self.num_clients += 1
        while True:
            try:
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
                            self.workspace = Path(helpers.parse_uri(message["params"]["rootUri"], encoding=self._encoding))
                            self._logger.info("Client workspace folder: %s", self.workspace)
                            client_options = message.get("params", {}).get("capabilities", {})
                            announcement = self.initialize(client_options)
                            await self.send_response(message["id"], announcement, writer)
                        elif has_started and method == "shutdown":
                            self._logger.info("Client requested shutdown")
                            await self.send_response(message["id"], {}, writer)
                            # explicitly clear the dirty files on shutdown
                            dirty_files.clear()
                        elif has_started and method == "textDocument/completion":
                            file_uri = message.get("params", {}).get("textDocument", {}).get("uri", None)
                            if file_uri:
                                document = self._get_document(file_uri, dirty_files)
                                completions = await self.provide_code_completion(message["params"], document)
                                await self.send_response(message["id"], completions, writer)
                        elif has_started and method == "textDocument/definition":
                            file_uri = message.get("params", {}).get("textDocument", {}).get("uri", None)
                            if file_uri:
                                document = self._get_document(file_uri, dirty_files)
                                definition = await self.provide_definition(message["params"], document)
                                await self.send_response(message["id"], definition, writer)
                        # elif has_started and method == "textDocument/documentHighlight":
                        #     highlights = await self.provide_highlight(message["params"])
                        #     await self.send_response(message["id"], highlights, writer)
                        elif has_started and method == "textDocument/hover":
                            file_uri = message.get("params", {}).get("textDocument", {}).get("uri", None)
                            if file_uri:
                                document = self._get_document(file_uri, dirty_files)
                                hovers = await self.provide_hover(message["params"], document)
                                await self.send_response(message["id"], hovers, writer)
                        elif has_started and method == "textDocument/references":
                            file_uri = message.get("params", {}).get("textDocument", {}).get("uri", None)
                            if file_uri:
                                document = self._get_document(file_uri, dirty_files)
                                references = await self.provide_reference(message["params"], document)
                                await self.send_response(message["id"], references, writer)
                        elif has_started and method == "textDocument/rename":
                            file_uri = message.get("params", {}).get("textDocument", {}).get("uri", None)
                            if file_uri:
                                document = self._get_document(file_uri, dirty_files)
                                renames = await self.provide_rename(message["params"], document)
                                await self.send_response(message["id"], renames, writer)
                        elif has_started and method == "workspace/executeCommand":
                            cmd = message.get("params", {}).get("command", "")
                            args = message.get("params", {}).get("arguments", [])
                            if cmd == "yara.CompileRule":
                                self._logger.info("Compiling rule per user's request")
                            elif cmd == "yara.CompileAllRules":
                                self._logger.info("Compiling all rules in %s per user's request", self.workspace)
                                files = [str(i.resolve()) for i in self.workspace.glob("**/*.yara")]
                                files.extend([str(i.resolve()) for i in self.workspace.glob("**/*.yar")])
                                for file_path in files:
                                    with open(file_path, "rb") as ifile:
                                        document = ifile.read().decode(self._encoding)
                                        diagnostics = await self.provide_diagnostic(document)
                                        if diagnostics:
                                            file_uri = helpers.create_file_uri(file_path)
                                            params = {
                                                "uri": file_uri,
                                                "diagnostics": diagnostics
                                            }
                                            await self.send_notification("textDocument/publishDiagnostics", params, writer)
                            else:
                                self._logger.warning("Unknown command: %s [%s]", cmd, ",".join(args))
                    # if no id is present, this is a JSON-RPC notification
                    else:
                        if method == "initialized":
                            self._logger.info("Client has been successfully initialized")
                            has_started = True
                            params = {"type": lsp.MessageType.INFO, "message": "Successfully connected"}
                            await self.send_notification("window/showMessageRequest", params, writer)
                        elif has_started and method == "exit":
                            self._logger.info("Server exiting process per client request")
                            # first remove the client associated with this handler
                            await self.remove_client(writer)
                            raise ce.ServerExit("Server exiting process per client request")
                            # # then clean up all the remaining tasks
                            loop = asyncio.get_event_loop()
                            for task in asyncio.Task.all_tasks(loop=loop):
                                task.cancel()
                            # # finally, stop the server
                            loop.stop()
                            loop.close()
                        elif has_started and method == "workspace/didChangeConfiguration":
                            config = message.get("params", {}).get("settings", {}).get("yara", {})
                            self._logger.debug("Changed workspace config to %s", json.dumps(config))
                        elif has_started and method == "textDocument/didChange":
                            file_uri = message.get("params", {}).get("textDocument", {}).get("uri", None)
                            if file_uri:
                                self._logger.debug("Adding %s to dirty files list", file_uri)
                                for changes in message.get("params", {}).get("contentChanges", []):
                                    # full text is submitted with each change
                                    change = changes.get("text", None)
                                    if change:
                                        dirty_files[file_uri] = change
                        elif has_started and method == "textDocument/didClose":
                            file_uri = message.get("params", {}).get("textDocument", {}).get("uri", "")
                            # file is no longer dirty after closing
                            if file_uri in dirty_files:
                                del dirty_files[file_uri]
                                self._logger.debug("Removed %s from dirty files list", file_uri)
                        elif has_started and method == "textDocument/didSave":
                            file_uri = message.get("params", {}).get("textDocument", {}).get("uri", "")
                            # file is no longer dirty after saving
                            if file_uri in dirty_files:
                                del dirty_files[file_uri]
                                self._logger.debug("Removed %s from dirty files list", file_uri)
                            if config.get("compile_on_save", False):
                                file_path = helpers.parse_uri(file_uri)
                                with open(file_path, "rb") as ifile:
                                    document = ifile.read().decode(self._encoding)
                                diagnostics = await self.provide_diagnostic(document)
                                params = {
                                    "uri": file_uri,
                                    "diagnostics": diagnostics
                                }
                                await self.send_notification("textDocument/publishDiagnostics", params, writer)
            except ce.NoYaraPython as err:
                self._logger.warning(err)
                params = {
                    "type": lsp.MessageType.WARNING,
                    "message": err
                }
                await self.send_notification("window/showMessage", params, writer)
            except (ce.CodeCompletionError, ce.DefinitionError, ce.DiagnosticError, \
                    ce.HighlightError, ce.HoverError, ce.RenameError, ce.SymbolReferenceError) as err:
                self._logger.error(err)
                params = {
                    "type": lsp.MessageType.ERROR,
                    "message": str(err)
                }
                await self.send_notification("window/showMessage", params, writer)

    def initialize(self, client_options: dict) -> dict:
        '''Announce language support methods

        :client_options: Dictionary of registration options that the client supports
        '''
        doc_options = client_options.get("textDocument", {})
        ws_options = client_options.get("workspace", {})
        server_options = {}
        if doc_options.get("completion", {}).get("dynamicRegistration", False):
            server_options["completionProvider"] = {
                # The server does not provide support to resolve additional information for a completion item
                "resolveProvider": False,
                "triggerCharacters": ["."]
            }
        if doc_options.get("definition", {}).get("dynamicRegistration", False):
            server_options["definitionProvider"] = True
        # if doc_options.get("documentHighlight", {}).get("dynamicRegistration", False):
        #     server_options["documentHighlightProvider"] = True
        if doc_options.get("hover", {}).get("dynamicRegistration", False):
            server_options["hoverProvider"] = True
            self.hover_langs = doc_options.get("hover", {}).get("contentFormat", self.hover_langs)
        if ws_options.get("executeCommand", {}).get("dynamicRegistration", False):
            server_options["executeCommandProvider"] = {
                "commands": []
            }
            if HAS_YARA:
                server_options["executeCommandProvider"]["commands"].append("yara.CompileRule")
                server_options["executeCommandProvider"]["commands"].append("yara.CompileAllRules")
        # if doc_options.get("formatting", {}).get("dynamicRegistration", False):
        #     server_options["documentFormattingProvider"] = True
        if doc_options.get("references", {}).get("dynamicRegistration", False):
            server_options["referencesProvider"] = True
        # if doc_options.get("rename", {}).get("dynamicRegistration", False):
        #     server_options["renameProvider"] = True
        if doc_options.get("synchronization", {}).get("dynamicRegistration", False):
            # Documents are synced by always sending the full content of the document
            server_options["textDocumentSync"] = lsp.TextSyncKind.FULL
        return {"capabilities": server_options}

    async def provide_code_completion(self, params: dict, document: str) -> list:
        '''Respond to the completionItem/resolve request

        Returns a (possibly empty) list of completion items
        '''
        try:
            results = []
            trigger = params.get("context", {}).get("triggerCharacter", ".")
            # typically the trigger is at the end of a line, so subtract one to avoid an IndexError
            pos = lsp.Position(line=params["position"]["line"], char=params["position"]["character"]-1)
            symbol = helpers.resolve_symbol(document, pos)
            if not symbol:
                return []
            # split up the symbols into component parts, leaving off the last trigger character
            symbols = symbol.split(trigger)
            schema = self.modules
            for depth, symbol in enumerate(symbols):
                if symbol in schema:
                    # if we're at the last symbol, return completion items
                    if depth == len(symbols) - 1:
                        completion_items = schema.get(symbol, {})
                        if isinstance(completion_items, dict):
                            for label, kind_str in completion_items.items():
                                kind = lsp.CompletionItemKind.CLASS
                                if str(kind_str).lower() == "enum":
                                    kind = lsp.CompletionItemKind.ENUM
                                elif str(kind_str).lower() == "property":
                                    kind = lsp.CompletionItemKind.PROPERTY
                                elif str(kind_str).lower() == "method":
                                    kind = lsp.CompletionItemKind.METHOD
                                results.append(lsp.CompletionItem(label, kind))
                    else:
                        schema = schema[symbol]
            return results
        except Exception as err:
            raise ce.CodeCompletionError("Could not offer completion items: {}".format(err))

    async def provide_definition(self, params: dict, document: str) -> list:
        '''Respond to the textDocument/definition request

        Returns a (possibly empty) list of symbol Locations
        '''
        results = []
        file_uri = params.get("textDocument", {}).get("uri", None)
        pos = lsp.Position(line=params["position"]["line"], char=params["position"]["character"])
        symbol = helpers.resolve_symbol(document, pos)
        if not symbol:
            return []
        try:
            # check to see if the symbol is a variable or a rule name (currently the only valid symbols)
            if symbol[0] in self._varchar:
                pattern = "\\${} =\\s".format("".join(symbol[1:]))
                rule_range = helpers.get_rule_range(document, pos)
                match_lines = document.split("\n")[rule_range.start.line:rule_range.end.line+1]
                rel_offset = rule_range.start.line
            # else assume this is a rule symbol
            else:
                pattern = "\\brule {}\\b".format(symbol)
                match_lines = document.split("\n")
                rel_offset = 0

            for index, line in enumerate(match_lines):
                for match in re.finditer(pattern, line):
                    if match:
                        offset = rel_offset + index
                        locrange = lsp.Range(
                            start=lsp.Position(line=offset, char=match.start()),
                            end=lsp.Position(line=offset, char=match.end())
                        )
                        results.append(lsp.Location(locrange, file_uri))
            return results
        except re.error:
            self._logger.debug("Error building regex pattern: %s", pattern)
            return []
        except Exception as err:
            raise ce.DefinitionError("Could not offer definition for symbol '{}': {}".format(symbol, err))

    async def provide_diagnostic(self, document: str) -> list:
        ''' Respond to the textDocument/publishDiagnostics request

        :document: Contents of YARA rule file
        '''
        try:
            if HAS_YARA:
                diagnostics = []
                try:
                    yara.compile(source=document)
                except yara.SyntaxError as error:
                    line_no, msg = helpers.parse_result(str(error))
                    # VSCode is zero-indexed
                    line_no -= 1
                    first_char = helpers.get_first_non_whitespace_index(document.split("\n")[line_no])
                    symbol_range = lsp.Range(
                        start=lsp.Position(line_no, first_char),
                        end=lsp.Position(line_no, 10000)
                    )
                    diagnostics.append(
                        lsp.Diagnostic(
                            locrange=symbol_range,
                            severity=lsp.DiagnosticSeverity.ERROR,
                            message=msg
                        )
                    )
                except yara.WarningError as warning:
                    line_no, msg = helpers.parse_result(str(warning))
                    # VSCode is zero-indexed
                    line_no -= 1
                    first_char = helpers.get_first_non_whitespace_index(document.split("\n")[line_no])
                    symbol_range = lsp.Range(
                        start=lsp.Position(line_no, first_char),
                        end=lsp.Position(line_no, 10000)
                    )
                    diagnostics.append(
                        lsp.Diagnostic(
                            locrange=symbol_range,
                            severity=lsp.DiagnosticSeverity.WARNING,
                            message=msg
                        )
                    )
                return diagnostics
            else:
                if self.diagnostics_warned:
                    pass
                else:
                    self.diagnostics_warned = True
                    raise ce.NoYaraPython("yara-python is not installed. Diagnostics and Compile commands are disabled")
        except Exception as err:
            raise ce.DiagnosticError("Could not compile rule: {}".format(err))

    async def provide_highlight(self, params: dict, document: str) -> list:
        ''' Respond to the textDocument/documentHighlight request '''
        try:
            self._logger.warning("provide_highlight() is not implemented")
            results = []
            return results
        except Exception as err:
            raise ce.HighlightError("Could not offer code highlighting: {}".format(err))

    async def provide_hover(self, params: dict, document: str) -> list:
        ''' Respond to the textDocument/hover request '''
        try:
            definitions = await self.provide_definition(params, document)
            if len(definitions) > 0:
                # only care about the first definition; although there shouldn't be more
                try:
                    definition = definitions[0]
                    line = document.split("\n")[definition.range.start.line]
                    value = line.split(" = ")[1]
                    contents = lsp.MarkupContent(lsp.MarkupKind.Plaintext, content=value)
                    return lsp.Hover(contents)
                except IndexError as err:
                    self._logger.error(err)
            return None
        except Exception as err:
            raise ce.HoverError("Could not offer definition hover: {}".format(err))

    async def provide_reference(self, params: dict, document: str) -> list:
        '''The references request is sent from the client to the server to resolve project-wide references for the symbol denoted by the given text document position

        Returns a (possibly empty) list of symbol Locations
        '''
        results = []
        file_uri = params.get("textDocument", {}).get("uri", None)
        pos = lsp.Position(line=params["position"]["line"], char=params["position"]["character"])
        symbol = helpers.resolve_symbol(document, pos)
        if not symbol:
            return []
        try:
            # check to see if the symbol is a variable or a rule name (currently the only valid symbols)
            if symbol[0] in self._varchar:
                # gotta match the wildcard variables too
                if symbol[-1] == "*":
                    symbol = symbol.replace("*", ".*?")
                # any possible first character matching self._varchar must be treated as a reference
                pattern = "[{}]{}\\b".format("".join(self._varchar), "".join(symbol[1:]))
                rule_range = helpers.get_rule_range(document, pos)
                rule_lines = document.split("\n")[rule_range.start.line:rule_range.end.line+1]
                rel_offset = rule_range.start.line
            else:
                rel_offset = 0
                pattern = "{}\\b".format(symbol)
                rule_lines = document.split("\n")

            for index, line in enumerate(rule_lines):
                for match in re.finditer(pattern, line):
                    if match:
                        # index corresponds to line no. within each rule, not within file
                        offset = rel_offset + index
                        locrange = lsp.Range(
                            start=lsp.Position(line=offset, char=match.start()),
                            end=lsp.Position(line=offset, char=match.end())
                        )
                        results.append(lsp.Location(locrange, file_uri))
            return results
        except re.error:
            self._logger.debug("Error building regex pattern: %s", pattern)
            return []
        except Exception as err:
            raise ce.SymbolReferenceError("Could not find references for '{}': {}".format(symbol, err))

    async def provide_rename(self, params: dict, document: str) -> list:
        ''' Respond to the textDocument/rename request '''
        try:
            self._logger.warning("provide_rename() is not implemented")
            results = []
        # file_uri = params.get("textDocument", {}).get("uri", None)
        # pos = lsp.Position(line=params["position"]["line"], char=params["position"]["character"])
        # old_text = helpers.resolve_symbol(document, pos)
        # new_text = params.get("newName", None)
        # if new_text is None:
        #     self._logger.warning("No text to rename symbol to. Skipping")
        #     return []
        # elif new_text == old_text:
        #     self._logger.warning("New rename symbol is the same as the old. Skipping")
        #     return []
        # elif old_text.endswith("*"):
        #     self._logger.warning("Cannot rename wildcard symbols. Skipping")
        #     return []
        # # let provide_reference() determine symbol or rule
        # # and therefore what scope to look into
        # refs = await self.provide_reference(params, document)
        # edits = [lsp.TextEdit(ref.range, new_text) for ref in refs]
        # results.append(lsp.WorkspaceEdit(changes=edits))
        # if len(results) > 0:
        #     return results
        # else:
        #     self._logger.warning("No symbol references found to rename. Skipping")
            return results
        except Exception as err:
            raise ce.RenameError("Could not rename symbol: {}".format(err))

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
            self._logger.debug("input <= %r", data)
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
        self._logger.debug("output => %r", message.encode(self._encoding))
        writer.write("Content-Length: {:d}\r\n\r\n{:s}".format(len(message), message).encode(self._encoding))
        await writer.drain()
