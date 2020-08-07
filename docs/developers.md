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
There is now a `setup.py` installation package as well, that is best built with `pip wheel` and installed in the local venv.
```text
~$ cd vscode-yara/
~/vscode-yara$ npm install
~/vscode-yara$ cd server/
~/vscode-yara/server$ python3 -m venv ./env
~/vscode-yara/server$ source ./env/bin/activate
(env) ~/vscode-yara/server$ python3 -m pip install yara-python wheel
(env) ~/vscode-yara/server$ python3 -m pip wheel .
(env) ~/vscode-yara/server$ python3 -m pip install yarals
```

## Execution
To begin testing, use the `vscode_yara.py` script, which will instantiate the event loop and start the server.

Once the server is up and running, open up VSCode and start a Debugging terminal using the `Launch Extension` configuration. Typically, pressing F5 in VSCode will do this all for you.

Once it starts running, you'll see a message showing the server has started up, like below:

```text
(env) ~/vscode-yara$ python3 ./server/vscode_yara.py
yara.runner | Starting YARA IO language server
yara.runner | Serving on tcp://127.0.0.1:8471
```

## Logging
The `vscode_yara.py` script is configured to print info, error, warning, and critical logs to the screen. Debug logs (mostly raw json-rpc messages) are also written to a `.yara.log` file in the root folder of the repository.

The Python [logging](https://docs.python.org/3/library/logging.html) module is used to control these logs, so feel free to play with it until it works for you.


## Testing
Unit tests are provided for the Python code in the  `server/tests/` directory.

I've tried addding tests for every function - both positive and negative tests - in the `test_server.py` and `test_protocol.py` scripts. The `asyncio`-specific tests require some work (namely transports and handling errors), but the other modules have little to no coverage. If you want to add to the test coverage, I'm more than happy to take pull requests!

To run tests for any given module, run the `test_<module>.py` file directly (just for now - I'm still learning good test practices). Alternatively, all tests can be run at once using the `unittest` module's discover feature, like below:

```text
(env) ~/vscode-yara$ python -m unittest discover .\server\tests

FF............FF..........F
```

Each module's test verbosity can be changed like below:

```text
(env) ~/vscode-yara$ python .\server\tests\test_protocol.py

----------------------------------------------------------------------
Ran 5 tests in 0.004s

OK
ProtocolTests coverage: 100.0%
```

```text
(env) ~/vscode-yara$ python .\server\tests\test_protocol.py -v

.....
----------------------------------------------------------------------
Ran 5 tests in 0.000s

OK
ProtocolTests coverage: 100.0%
```

```text
(env) ~/vscode-yara$ python .\server\tests\test_protocol.py -vv

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

[logo]: https://raw.githubusercontent.com/infosec-intern/vscode-yara/main/images/logo.png "Source Image from blacktop/docker-yara"
