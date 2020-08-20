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
(env) ~/vscode-yara/server$ python3 -m pip install yara-python wheel pytest pytest-asyncio
(env) ~/vscode-yara/server$ python3 -m pip wheel .
(env) ~/vscode-yara/server$ python3 -m pip install yarals
```

## Execution

To begin testing, create a [Launch Configuration](https://code.visualstudio.com/docs/editor/multi-root-workspaces#_workspace-launch-configurations) entry and point it to the compiled Javascript found in `${workspaceRoot}/out/client/extension.js`.

This entry will allow VSCode to start the client, which should install and start the language server automatically and allow for you to test. Typically, pressing F5 in VSCode will trigger this action.

Once it starts running, you'll see a message in the log file showing the server has started up, like below:

```text
yara.runner | Starting YARA IO language server
yara.runner | Serving on tcp://127.0.0.1:8471
```

## Logging

The `vscode_yara.py` script is configured to print info, error, warning, and critical logs to the screen. Debug logs (mostly raw json-rpc messages) are also written to a `.yara.log` file in the root folder of the repository.

The Python [logging](https://docs.python.org/3/library/logging.html) module is used to control these logs, so feel free to play with it until it works for you.

## Testing

Unit tests are provided for the Python code in the  `server/tests/` directory using the `pytest` and `pytest-asyncio` packages.

I've tried adding tests for every function in the `test_*.py` scripts, with the specific module name represented in the test filename (i.e. `protocol.py` tests are found in `test_protocol.py`). If you want to add to the test coverage, I'm more than happy to take pull requests!

To run tests for any given module, activate the Python virtual environment and run `pytest test_<module>.py`. Alternatively, all tests can be run at once using the `pytest` module's discover feature, like below:

```text
(env) ~/vscode-yara$ pytest

 pytest
======= test session starts =======
platform linux -- Python 3.8.2, pytest-6.0.1, py-1.9.0, pluggy-0.13.1
rootdir: /vscode-yara
plugins: asyncio-0.14.0
collected 46 items

server/tests/test_config.py ..                                  [  4%]
server/tests/test_helpers.py ......s.                           [ 21%]
server/tests/test_protocol.py .....                             [ 32%]
server/tests/test_server.py sss...............s..........       [ 95%]
server/tests/test_transport.py ..                               [100%]
======= 41 passed, 5 skipped in 0.54s =======
```

Each module can be tested like below:

```text
(env) ~/vscode-yara$ pytest ./server/tests/test_config.py
======= test session starts =======
platform linux -- Python 3.8.2, pytest-6.0.1, py-1.9.0, pluggy-0.13.1
rootdir: /vscode-yara/server
plugins: asyncio-0.14.0
collected 2 items

server/tests/test_config.py ..                                  [100%]

======= 2 passed in 0.03s =======
```

And individual tests can be run using the `::` delimiter:

```text
$ pytest ./server/tests/test_config.py::test_compile_on_save_false
======= test session starts =======
platform linux -- Python 3.8.2, pytest-6.0.1, py-1.9.0, pluggy-0.13.1
rootdir: /vscode-yara/server
plugins: asyncio-0.14.0
collected 1 item

server/tests/test_config.py ..                                  [100%]

======= 1 passed in 0.02s =======
```

[logo]: https://raw.githubusercontent.com/infosec-intern/vscode-yara/main/images/logo.png "Source Image from blacktop/docker-yara"
