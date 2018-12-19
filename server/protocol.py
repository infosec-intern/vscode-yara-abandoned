''' VSCode Language Server Protocol Definitions

For more info: https://microsoft.github.io/language-server-protocol/specification
'''
import json
from typing import List, Union

EOL: List = ["\n", "\r\n", "\r"]
# Error codes defined by JSON RPC
METHOD_NOT_FOUND = -32601
INTERNAL_ERROR = -32603
INVALID_PARAMS = -32602
INVALID_REQUEST = -32600
PARSE_ERROR = -32700
SERVER_ERROR_START = -32099
SERVER_ERROR_END = -32000
SERVER_NOT_INITIALIZED = -32002
UNKNOWN_ERROR_CODE = -32001
# Defined by the protocol.
REQUEST_CANCELLED = -32800
# DiagnosticSeveriy
DIAGNOSTIC_ERROR = 1
DIAGNOSTIC_WARNING = 2
DIAGNOSTIC_INFO = 3
DIAGNOSTIC_HINT = 4
# MessageType
MESSAGETYPE_ERROR = 1
MESSAGETYPE_WARNING = 2
MESSAGETYPE_INFO = 3
MESSAGETYPE_LOG = 4
# TransportKind
TRANSPORTKIND_NONE = 0
TRANSPORTKIND_FULL = 1
TRANSPORTKIND_INC = 2

class Position(object):
    def __init__(self, line: int, char: int):
        ''' Line position in a document (zero-based)

        Character offset on a line in a document (zero-based). Assuming that the line is
        represented as a string, the `character` value represents the gap between the
        `character` and `character + 1`.

        If the character value is greater than the line length it defaults back to the
        line length.
        '''
        self.line = line
        self.char = char

class Range(object):
    def __init__(self, start: Position, end: Position):
        ''' A range in a text document expressed as (zero-based) start and end positions

        A range is comparable to a selection in an editor. Therefore the end position is exclusive
        '''
        self.start = start
        self.end = end

class Location(object):
    def __init__(self, locrange: Range, uri: str):
        ''' Represents a location inside a resource
        such as a line inside a text file
        '''
        self.range = locrange
        self.uri = uri

class Diagnostic(object):
    def __init__(self, locrange: Range, severity: DiagnosticSeverity, code: Union[int,str], message: str, source: str="yara", relatedInformation: List=[]):
        ''' Represents a diagnostic, such as a compiler error or warning

        Diagnostic objects are only valid in the scope of a resource.
        '''
        self.code = code
        self.message = message
        self.range = locrange
        self.relatedInformation = relatedInformation
        self.severity = severity
        self.source = source