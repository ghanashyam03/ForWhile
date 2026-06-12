class ForWhileError(Exception):
    """Base class for ForWhile exceptions."""
    def __init__(self, message, line=None):
        super().__init__(message)
        self.message = message
        self.line = line

    def __str__(self):
        if self.line is not None:
            return f"[Story Error] {self.message} (line {self.line})"
        return f"[Story Error] {self.message}"

class ForWhileSyntaxError(ForWhileError):
    """Raised when a syntax/parse error occurs."""
    pass

class ForWhileRuntimeError(ForWhileError):
    """Raised when a runtime execution error occurs."""
    pass
