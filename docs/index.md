![][logo]

# YARA for Visual Studio Code
Rich language support for the YARA pattern matching language

This repository was formerly listed as [textmate-yara](https://github.com/infosec-intern/textmate-yara). It is being moved to [vscode-yara](https://github.com/infosec-intern/vscode-yara) to keep more in-line with the features provided by the extension. It is now more than just colorization support, and I believe the title should reflect that.

## Features

* [Code Completion](./features/code_completion.md)
* [Commands](./features/commands.md)
* [Definitions](./features/definitions.md)
* [Diagnostics](./features/diagnostics.md)
* [Hovers](./features/hovers.md)
* [References](./features/references.md)

### Snippets

Some common sequences are provided as snippets, to allow easy auto-completion for things like:
* rule skeletons
* for loops
* `meta:`, `strings:`, and `condition:` blocks
* import statements for standard modules
* "any" and "all" keywords

## Requirements
With the new language server protocol, Python 3.7 or higher is required, due to the heavy use of the `asyncio` library and certain specific, related functions being used.

In addition, `yara-python` must be installed. If it is not installed, this extension will try to build a virtual environment in `$EXTENSIONROOT/server/env` with the latest Python version and install dependencies there.

**Note:** If you are on Windows, you might have to set the `$INCLUDE` environment variable before buidling this environment, so that when `yara-python` is compiled for your local system, Python knows where to find the appropriate DLLs.
On Windows 10, this would probably look like:
```powershell
> set INCLUDE="C:\Program Files (x86)\Windows Kits\10\Include"
> py -3 -m pip install yara-python
```

## Developers
If you want to build this locally for development purposes (or testing out cutting edge features)
please follow the steps at [Developers](./developers.md)

## Problems?
If you encounter an issue with the syntax, feel free to create an issue or pull request!
Alternatively, check out some of the YARA syntaxes for Sublime and Atom, or the one bundled with YARA itself.
They use the same syntax engine as VSCode and should work the same way.

## YARA Documentation
* [YARA Documentation](https://yara.readthedocs.io/)

## Language Server Protocol
* [JSON RPC Specification](https://www.jsonrpc.org/specification)
* [Language Server Protocol Specification](https://microsoft.github.io/language-server-protocol/specification)
* [VSCode Example Language Server](https://code.visualstudio.com/docs/extensions/example-language-server)

[logo]: https://raw.githubusercontent.com/infosec-intern/vscode-yara/main/images/logo.png "Source Image from blacktop/docker-yara"
