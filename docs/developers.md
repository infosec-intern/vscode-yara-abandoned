![][logo]

# Developers
If you want to build this locally for development purposes (or testing out cutting edge features) you've come to the right place!

## Getting Started
To get the files, clone the git repository to your local filesystem. All the commands below are done in a Bash prompt on Linux. PowerShell on Windows should be largely the same, with maybe some minor tweaks to the Python commands.
```text
~$ git clone https://github.com/infosec-intern/vscode-yara.git
~$ cd vscode-yara/
~/vscode-yara$ git checkout language-server
```

## Installation
Local installation consists of installing client and server dependencies for Node.js and Python, respectively.
```text
~$ cd vscode-yara/
~/vscode-yara$ npm install
~/vscode-yara$ cd server/
~/vscode-yara/server$ python3 -m venv ./env
~/vscode-yara/server$ source ./env/bin/activate
(env) ~/vscode-yara/server$ python3 -m pip install yara-python
```

## Execution
To begin testing, use the `runner.py` script, which will instantiate the event loop and start the server.

Once the server is up and running, open up VSCode and start a Debugging terminal using the `Launch Extension` configuration. Typically, pressing F5 in VSCode will do this all for you.

Once it starts running, you'll see a message showing the server has started up, like below:

```text
(env) ~/vscode-yara$ python3 ./server/runner.py
yara.runner | Starting YARA IO language server
yara.runner | Serving on tcp://127.0.0.1:8471
```

## Logging
The `runner.py` script is configured to print info, error, warning, and critical logs to the screen. Debug logs (mostly raw json-rpc messages) are also written to a `.yara.log` file in the root folder of the repository.

The Python [logging](https://docs.python.org/3/library/logging.html) module is used to control these logs, so feel free to play with it until it works for you.


## Testing
Unit tests are provided for the Python code in the various `test_*.py` files.

I've tried addding tests for every function - both positive and negative tests - in the `test_server.py` and `test_protocol.py` scripts. The other modules have little to no coverage. If you want to add to the test coverage, I'm more than happy to take pull requests!

To run tests for any given module, run the `test_<module>.py` file directly (just for now - I'm still learning good test practices). Output verbosity can be changed using the `-v` flag. Up to 2 flags can be provided to increase verbosity, such as `-vv`.

```text
(env) ~/vscode-yara$ python .\server\test_protocol.py -h

usage: Run protocol.py tests [-h] [-v]

optional arguments:
  -h, --help  show this help message and exit
  -v          Change test verbosity
```

Changing verbosity looks like the following:

```text
(env) ~/vscode-yara$ python .\server\test_protocol.py

----------------------------------------------------------------------
Ran 5 tests in 0.004s

OK
ProtocolTests coverage: 100.0%
```

```text
(env) ~/vscode-yara$ python .\server\test_protocol.py -v

.....
----------------------------------------------------------------------
Ran 5 tests in 0.000s

OK
ProtocolTests coverage: 100.0%
```

```text
(env) ~/vscode-yara$ python .\server\test_protocol.py -vv

test_completionitem (__main__.ProtocolTests)
Ensure CompletionItem is properly encoded to JSON dictionaries ... ok
test_diagnostic (__main__.ProtocolTests)
Ensure Diagnostic is properly encoded to JSON dictionaries ... ok
test_location (__main__.ProtocolTests)
Ensure Location is properly encoded to JSON dictionaries ... ok
test_position (__main__.ProtocolTests)
Ensure Position is properly encoded to JSON dictionaries ... ok
test_range (__main__.ProtocolTests)
Ensure Range is properly encoded to JSON dictionaries ... ok

----------------------------------------------------------------------
Ran 5 tests in 0.004s

OK
ProtocolTests coverage: 100.0%
```

[logo]: ../images/logo.png "Source Image from blacktop/docker-yara"
