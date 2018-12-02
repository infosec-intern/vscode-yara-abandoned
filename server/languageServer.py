''' Implements a VSCode language server for YARA '''
import asyncio
import http
import json
import logging


logging.basicConfig(level=logging.INFO, format="%(levelname)s [%(module)s:$(lineno)d] %(message)s")

try:
    import yara
    HAS_YARA = True
except ModuleNotFoundError:
    # set INCLUDE="C:\Program Files (x86)\Windows Kits\10\Include" && python -m pip install yara-python
    HAS_YARA = False


async def stream_handler(message, port=8888):
    reader, writer = await asyncio.open_connection("127.0.0.1", port)
    print(reader)
    print(writer)
    data = await reader.read(100)
    print("Received: {:r}".format(data.decode()))
    print("Close the connection")
    writer.close()
    await writer.wait_closed()

def code_completion_provider(request: dict):
    ''' Respond to the completionItem/resolve request '''
    logging.warning("code_completion_provider() is not yet implemented")

def definition_provider(request: dict):
    ''' Respond to the textDocument/definition request '''
    logging.warning("definition_provider() is not yet implemented")
    return {
        "jsonrpc": "2.0",
        "id": request["id"],
        "result": {}
    }

def diagnostic_provider(request: dict):
    ''' Respond to the textDocument/publishDiagnostics request
    The message carries an array of diagnostic items for a resource URI.
    '''
    if HAS_YARA:
        logging.warning("diagnostic_provider() is not yet implemented")
        logging.debug("yara-python is installed")
        response = {
            "jsonrpc": "2.0",
            "id": request["id"],
            "result": {}
        }
    elif not HAS_YARA:
        logging.error("yara-python is not installed. Diagnostics are disabled")
        response = {}
    return response

def highlight_provider(request: dict):
    ''' Respond to the textDocument/documentHighlight request '''
    logging.warning("highlight_provider() is not implemented")
    return {
        "jsonrpc": "2.0",
        "id": request["id"],
        "result": {}
    }

def reference_provider(request: dict):
    ''' Respond to the textDocument/references request '''
    logging.warning("reference_provider() is not yet implemented")
    return {
        "jsonrpc": "2.0",
        "id": request["id"],
        "result": {}
    }

def rename_provider(request: dict):
    ''' Respond to the textDocument/rename request '''
    logging.warning("rename_provider() is not yet implemented")
    return {
        "jsonrpc": "2.0",
        "id": request["id"],
        "result": {}
    }

def initialize():
    ''' Announce language support methods '''
    # document_selector = { "language": "yara", "scheme": "file" }
    announcement = {
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
    }

    return json.dumps(announcement)
