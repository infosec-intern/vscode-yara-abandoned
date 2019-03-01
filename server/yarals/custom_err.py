class ServerExit(Exception):
    pass

class CodeCompletionError(Exception):
    pass

class DefinitionError(Exception):
    pass

class DiagnosticError(Exception):
    pass

class HighlightError(Exception):
    pass

class HoverError(Exception):
    pass

class NoYaraPython(Exception):
    pass

class RenameError(Exception):
    pass

class SymbolReferenceError(Exception):
    pass
