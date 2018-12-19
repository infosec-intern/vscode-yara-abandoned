''' Various utility functions that don't quite fit elsewhere '''
import re

from urllib.parse import unquote, urlsplit
import protocol as lsp


def parse_uri(file_uri: str, encoding="utf-8"):
    return urlsplit(unquote(file_uri, encoding=encoding)).path

def resolve_symbol(file_path: str, pos: lsp.Position, encoding="utf-8") -> str:
    ''' Resolve a symbol located at the given position '''
    pass

def get_rule_range(file_path: str, pos: lsp.Position, encoding="utf-8") -> lsp.Range:
    ''' Get the start and end boundaries for the current YARA rule based on a symbol's position '''
    rule_start = re.compile("^rule ")
    rule_end = re.compile("^\}")
    with open(file_path, "rb", encoding=encoding) as document:
        for line in document.readlines():
            print(line)
