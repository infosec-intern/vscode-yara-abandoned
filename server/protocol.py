''' VSCode Language Server Protocol Definitions

For more info: https://microsoft.github.io/language-server-protocol/specification
'''
from enum import IntEnum
import json
from typing import List, Union

EOL: List = ["\n", "\r\n", "\r"]

# Protocol Constants
class CompletionTriggerKind(IntEnum):
    # Completion was triggered by typing an identifier (24x7 code
	# complete), manual invocation (e.g Ctrl+Space) or via API.
    INVOKED = 1
    # Completion was triggered by a trigger character specified by
	# the `triggerCharacters` properties of the `CompletionRegistrationOptions`
    CHARACTER = 2
    # Completion was re-triggered as the current completion list is incomplete.
    INCOMPLETE = 3

class JsonRPCError(IntEnum):
    METHOD_NOT_FOUND = -32601
    INTERNAL_ERROR = -32603
    INVALID_PARAMS = -32602
    INVALID_REQUEST = -32600
    PARSE_ERROR = -32700
    SERVER_ERROR_START = -32099
    SERVER_ERROR_END = -32000
    SERVER_NOT_INITIALIZED = -32002
    UNKNOWN_ERROR_CODE = -32001
    # Defined by the protocol
    REQUEST_CANCELLED = -32800

class DiagnosticSeverity(IntEnum):
    ERROR = 1
    WARNING = 2
    INFO = 3
    HINT = 4

class MessageType(IntEnum):
    ERROR = 1
    WARNING = 2
    INFO = 3
    LOG = 4

class TextSyncKind(IntEnum):
    NONE = 0
    FULL = 1
    INCREMENTAL = 2

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

    def __repr__(self):
        return "<Position(line={:d}, char={:d})>".format(self.line, self.char)

class Range(object):
    def __init__(self, start: Position, end: Position):
        ''' A range in a text document expressed as (zero-based) start and end positions

        A range is comparable to a selection in an editor. Therefore the end position is exclusive
        '''
        self.start = start
        self.end = end

    def __repr__(self):
        return "<Range(start={}, end={})>".format(self.start, self.end)

class Location(object):
    def __init__(self, locrange: Range, uri: str):
        ''' Represents a location inside a resource
        such as a line inside a text file
        '''
        self.range = locrange
        self.uri = uri

    def __repr__(self):
        return "<Location(range={}, uri={})>".format(self.range, self.uri)

class Diagnostic(object):
    def __init__(self, locrange: Range, severity: int, code: Union[int,str], message: str, source: str="yara", relatedInformation: List=[]):
        ''' Represents a diagnostic, such as a compiler error or warning

        Diagnostic objects are only valid in the scope of a resource.
        '''
        self.code = code
        self.message = message
        self.range = locrange
        self.relatedInformation = relatedInformation
        self.severity = severity
        self.source = source

    def __repr__(self):
        return "<Diagnostic(sev={:d}, code={}, msg={})>".format(self.severity, self.code, self.message)
