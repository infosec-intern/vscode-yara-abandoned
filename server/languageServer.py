''' Implements a VSCode language server for YARA '''
import asyncio
import http
import json
import logging
import sys


try:
    import yara
    HAS_YARA = True
except ModuleNotFoundError:
    # set INCLUDE="C:\Program Files (x86)\Windows Kits\10\Include" && python -m pip install yara-python
    logging.warning("yara-python not installed. Diagnostics will not be available")
    HAS_YARA = False


def _binary_stdio():
    '''
    Construct binary stdio streams (not text mode).
    This seems to be different for Window/Unix Python2/3, so going by:
        https://stackoverflow.com/questions/2850893/reading-binary-data-from-stdin

    Thanks Palantir!
    https://github.com/palantir/python-language-server/blob/ab3e5eaef848a0cc752110f85ed95187f5cffcc4/pyls/__main__.py
    '''
    if sys.version_info >= (3, 0):
        # pylint: disable=no-member
        stdin, stdout = sys.stdin.buffer, sys.stdout.buffer
    else:
        # Python 2 on Windows opens sys.stdin in text mode, and
        # binary data that read from it becomes corrupted on \r\n
        if sys.platform == "win32":
            # set sys.stdin to binary mode
            # pylint: disable=no-member,import-error
            import os
            import msvcrt
            msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
            msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
        stdin, stdout = sys.stdin, sys.stdout
    return stdin, stdout

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

def main():
    logging.info("Starting YARA IO language server")
    stdin, stdout = _binary_stdio()
    logging.debug("rfile: %s", stdin)
    logging.debug("wfile: %s", stdout)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s [%(module)s:%(lineno)d] %(message)s")
    main()
