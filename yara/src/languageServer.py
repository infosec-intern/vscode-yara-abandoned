''' Implements a VSCode language server for YARA '''
import asyncio

try:
    import yara
except ImportError:
    raise ImportError("yara-python is not installed")

print("yara-python is installed")
