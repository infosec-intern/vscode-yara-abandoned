''' Helper functions that don't quite fit elsewhere '''
import platform
import re
from typing import Tuple
from urllib.parse import quote, unquote, urlsplit

import protocol as lsp


def create_file_uri(path: str):
    '''Create a URI given a file path

    :path: Filepath to create a URI from
    '''
    return "file:///{}".format(quote(path, safe="/\\"))

def get_first_non_whitespace_index(line: str) -> int:
    '''Get the first non-whitespace character index in a given line

    :line: Text line to parse
    '''
    for index, char in enumerate(line):
        if char.strip():
            # self._logger.debug("first char is {} at position {:d}".format(char, index))
            return index

def get_rule_range(document: str, pos: lsp.Position) -> lsp.Range:
    '''Get the range of the YARA rule that a given symbol is in

    :document: Text to search in
               To determine line numbers, text is split at newlines, and carriage returns are ignored
    :pos: Symbol position to base range off of
    '''
    start_pattern = re.compile(r"^((private|global) )?rule\b")
    end_pattern = re.compile("^}$")
    start_pos = None
    end_pos = None
    lines = document.replace("\r", "").split("\n")
    # work backwards from the given position and find the start of rule
    for index in range(pos.line, 0, -1):
        line = lines[index]
        match = start_pattern.match(line)
        if match:
            start_pos = lsp.Position(line=index, char=0)
            break
    # start from the given position and find the first end of rule
    for index in range(pos.line, len(lines)):
        line = lines[index]
        match = end_pattern.match(line)
        if match:
            end_pos = lsp.Position(line=index, char=0)
            break
    return lsp.Range(start=start_pos, end=end_pos)

def parse_result(result: str) -> Tuple[int,str]:
    '''Parse the results from a YARA compilation attempt

    :result: Text to parse - takes the form:
            "line {number}: {message}"
    '''
    meta, message = tuple(result.split(":", maxsplit=1))
    _, line_no = tuple(meta.split(" "))
    return int(line_no), message.strip()

def parse_uri(uri: str, encoding="utf-8"):
    '''
    Parse a path out of a given uri

    :uri: URI string to be parsed
    :encoding: (Optional) string encoding to parse with
    '''
    file_path = urlsplit(unquote(uri, encoding=encoding)).path
    if platform.system() == "Windows":
        # urlsplit adds an extra slash to the beginning on windows
        return "".join(file_path[1:])
    else:
        return file_path

def resolve_symbol(document: str, pos: lsp.Position) -> str:
    '''Resolve a symbol located at the given position

    :document: Text to search in
               To determine line numbers, text is split at newlines, and carriage returns are ignored
    :pos: Symbol position to base range off of
    '''
    symbol_line = document.split("\n")[pos.line]
    line_end = len(symbol_line)
    # self._logger.debug("symbol line: %s", symbol_line)
    # find the left-bound of the symbol by looking backwards until a whitespace
    index = pos.char
    while True:
        if not symbol_line[index].strip():
            lb = index + 1
            break
        index -= 1
    # find the right-bound of the symbol by looking forwards until a whitespace
    index = pos.char
    while True:
        if index == line_end or not symbol_line[index].strip():
            rb = index
            break
        index += 1
    # self._logger.debug("symbol: %s", symbol_line[lb:rb])
    return symbol_line[lb:rb]
