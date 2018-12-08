![Source - https://raw.githubusercontent.com/blacktop/docker-yara/master/logo.png](./images/logo.png)

# YARA for Visual Studio Code
Language support for the YARA pattern matching language

## Screenshot
![Image as of 04 Sept 2016](./images/04092016.PNG)

## Features

### Diagnostics
The extension will compile workspace rules in the background and return errors and warnings as you type

### Definition Provider and Peeking
Allows peeking and Ctrl+clicking to jump to a rule definition. This applies to both rule names and variables

![Go To Definition](./images/peek_rules.PNG)

### Reference Provider
Shows the locations of a given symbol (rule name, variable, constant, etc.)

![Find All References](./images/references.PNG)

### Code Completion
Provides completion suggestions for standard YARA modules, including `pe`, `elf`, `math`, and all the others available in the official documentation: http://yara.readthedocs.io/en/v3.7.0/modules.html

![Code Completion](./images/module_completion.PNG)

### Snippets

## Requirements
With the new language server protocol, Python 3.5 or higher is required, due to the heavy use of the `asyncio` library.

In addition, `yara-python` must be installed. If it is not installed, this extension will try to build a virtual environment in `$EXTENSIONROOT/server/env` with the latest Python version and install dependencies there.

**Note:** If you are on Windows, you might have to set the `$INCLUDE` environment variable before buidling this environment, so that when `yara-python` is compiled for your local system, Python knows where to find the appropriate DLLs.
On Windows 10, this would probably look like:
```sh
set INCLUDE="C:\Program Files (x86)\Windows Kits\10\Include" && python -m pip install yara-python
```

## Problems?
If you encounter an issue with the syntax, feel free to create an issue or pull request!
Alternatively, check out some of the YARA syntaxes for Sublime and Atom, or the one bundled with YARA itself.
They use the same syntax engine as VSCode and should work the same way.

## YARA Documentation
https://yara.readthedocs.io/
