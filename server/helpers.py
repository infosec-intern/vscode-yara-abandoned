''' Helper functions that don't quite fit elsewhere '''
import re
from urllib.parse import unquote, urlsplit

import protocol as lsp


def parse_uri(uri: str, encoding="utf-8"):
    '''
    Parse a path out of a given uri

    :uri: URI string to be parsed
    :encoding: (Optional) string encoding to parse with
    '''
    return urlsplit(unquote(uri, encoding=encoding)).path

def resolve_symbol(document: str, pos: lsp.Position) -> str:
    '''Resolve a symbol located at the given position

    :document: Text to search in
               To determine line numbers, text is split at newlines, and carriage returns are ignored
    :pos: Symbol position to base range off of
    '''
    symbol = ""
    return symbol

def get_rule_range(document: str, pos: lsp.Position) -> lsp.Range:
    '''Get the start and end boundaries for the current YARA rule based on a symbol's position

    :document: Text to search in
               To determine line numbers, text is split at newlines, and carriage returns are ignored
    :pos: Symbol position to base range off of
    '''
    start_pattern = re.compile(r"^((private|global) )?rule ")
    start_pos = None
    end_pattern = re.compile(r"^}")
    end_pos = None
    lines = document.replace("\r", "").split("\n")
    # work backwards from the given position and find the start of rule
    for index in range(pos.line, 0, -1):
        line = lines[index]
        match = start_pattern.match(line)
        if match:
            start_pos = lsp.Position(line=index+1, char=0)
            break
    # start from the given position and find the first end of rule
    for index in range(pos.line, len(lines)):
        line = lines[index]
        match = end_pattern.match(line)
        if match:
            end_pos = lsp.Position(line=index+1, char=len(line)-1)
            break
    return lsp.Range(start=start_pos, end=end_pos)
