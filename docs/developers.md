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
Unit tests are provided for some of the Python code in the `unittests.py` script. I've tried addding tests for every function - both positive and negative tests - in the `server.py` and `protocol.py` scripts. The other modules have little to no coverage. If you want to add to the test coverage, I'm more than happy to take pull requests!

Flags are provided in the `unittests.py` for each test case.

```text
(env) ~/vscode-yara$ python ./server/unittests.py --help

usage: unittests.py [-h] [-a] [-c] [-e] [-p] [-s] [-t]

optional arguments:
  -h, --help       show this help message and exit
  -a, --all        Run all tests
  -c, --config     Run config tests
  -e, --helper     Run helper tests
  -p, --protocol   Run protocol tests
  -s, --server     Run server tests
  -t, --transport  Run transport tests
```

You can run the tests using the provided `unittests.py` file, which should look like so when complete:
```text
(env) ~/vscode-yara$ python ./server/unittests.py --all | grep coverage

Config test coverage: 0.0%
Helper test coverage: 100.0%
Protocol test coverage: 100.0%
Server test coverage: 76.9%
Transport test coverage: 50.0%
Total test coverage: 65.4%
```

[logo]: ../images/logo.png "Source Image from blacktop/docker-yara"
