''' VSCode Language Server Protocol Definitions

For more info: https://microsoft.github.io/language-server-protocol/specification
'''
from enum import Enum, IntEnum
import json
from typing import Union

EOL: list = ["\n", "\r\n", "\r"]

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

class CompletionItemKind(IntEnum):
    METHOD = 2
    CLASS = 7
    PROPERTY = 10
    ENUM = 13

class DiagnosticSeverity(IntEnum):
    ERROR = 1
    WARNING = 2
    INFO = 3
    HINT = 4

class MarkupKind(Enum):
    Markdown = "markdown"
    Plaintext = "plaintext"

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
        # rely on Python's runtime type conversions to ensure valid values are used
        self.line = int(line)
        self.char = int(char)

    def __repr__(self):
        return "<Position(line={:d}, char={:d})>".format(self.line, self.char)

class Range(object):
    def __init__(self, start: Position, end: Position):
        ''' A range in a text document expressed as (zero-based) start and end positions

        A range is comparable to a selection in an editor. Therefore the end position is exclusive
        '''
        if not isinstance(start, Position):
            raise TypeError("Start position cannot be {}. Must be Position".format(type(start)))
        elif not isinstance(end, Position):
            raise TypeError("End position cannot be {}. Must be Position".format(type(end)))
        self.start = start
        self.end = end

    def __repr__(self):
        return "<Range(start={}, end={})>".format(self.start, self.end)

class CompletionItem(object):
    def __init__(self, label: str, kind=CompletionItemKind.CLASS):
        ''' Suggested items for the programmer '''
        self.label = str(label)
        self.kind = int(kind)

    def __repr__(self):
        return "<CompletionItem(label={}, kind={:d})>".format(self.label, self.kind)

class Diagnostic(object):
    def __init__(self, locrange: Range, severity: int, message: str, relatedInformation: list=[]):
        ''' Represents a diagnostic, such as a compiler error or warning

        Diagnostic objects are only valid in the scope of a resource.
        '''
        self.message = str(message)
        if not isinstance(locrange, Range):
            raise TypeError("Location range cannot be {}. Must be Range".format(type(locrange)))
        self.range = locrange
        if not isinstance(relatedInformation, list):
            raise TypeError("Location range cannot be {}. Must be a list of strings".format(type(relatedInformation)))
        self.relatedInformation = relatedInformation
        self.severity = int(severity)

    def __repr__(self):
        return "<Diagnostic(severity={:d}, message={})>".format(self.severity, self.message)

class Location(object):
    def __init__(self, locrange: Range, uri: str):
        ''' Represents a location inside a resource
        such as a line inside a text file
        '''
        if not isinstance(locrange, Range):
            raise TypeError("Location range cannot be {}. Must be Range".format(type(locrange)))
        self.range = locrange
        self.uri = str(uri)

    def __repr__(self):
        return "<Location(range={}, uri={})>".format(self.range, self.uri)

class MarkupContent(object):
    def __init__(self, kind: MarkupKind, content: str):
        ''' Represents a string value which content
        is interpreted base on its kind flag
        '''
        if not isinstance(kind, MarkupKind):
            raise TypeError("Markup kind cannot be {}. Must be MarkupKind".format(type(kind)))
        self.kind = kind
        self.value = str(content)

class Hover(object):
    def __init__(self, contents: MarkupContent, locrange: Range=None):
        ''' Represents hover information at
        a given text document position
        '''
        if locrange:
            if not isinstance(locrange, Range):
                raise TypeError("Location range cannot be {}. Must be Range".format(type(locrange)))
            self.range = locrange
        if not isinstance(contents, MarkupContent):
            raise TypeError("Contents cannot be {}. Must be MarkupContent".format(type(contents)))
        self.contents = contents

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        ''' Custom JSON encoder '''
        if isinstance(obj, CompletionItem):
            return {
                "label": obj.label,
                "kind": obj.kind
            }
        elif isinstance(obj, Diagnostic):
            return {
                "message": obj.message,
                "range": obj.range,
                "relatedInformation": obj.relatedInformation,
                "severity": obj.severity
            }
        elif isinstance(obj, Hover):
            if hasattr(obj, "range"):
                return {
                    "range": obj.range,
                    "contents": obj.contents
                }
            else:
                return {
                    "contents": obj.contents
                }
        elif isinstance(obj, Location):
            return {
                "range": obj.range,
                "uri": obj.uri
            }
        elif isinstance(obj, MarkupContent):
            return {
                "kind": obj.kind,
                "value": obj.value
            }
        elif isinstance(obj, MarkupKind):
            return obj.value
        elif isinstance(obj, Position):
            return {
                "line": obj.line,
                "character": obj.char
            }
        elif isinstance(obj, Range):
            return {
                "start": obj.start,
                "end": obj.end
            }
        else:
            super().default(obj)
