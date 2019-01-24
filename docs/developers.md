![][logo]

# Developers
If you want to build this locally for development purposes (or testing out cutting edge features) you've come to the right place!

## Getting Started
To get the files, clone the git repository to your local filesystem. All the commands below are done in a Bash prompt on Linux. PowerShell on Windows should be largely the same, with maybe some minor tweaks to the Python commands.
```sh
$ git clone https://github.com/infosec-intern/vscode-yara.git
$ cd vscode-yara/
vscode-yara$ git checkout language-server
```

## Installation
Local installation consists of installing client and server dependencies for Node.js and Python, respectively.
```sh
$ cd vscode-yara/
vscode-yara$ npm install
vscode-yara$ cd server/
vscode-yara/server$ python3 -m venv ./env
vscode-yara/server$ source ./env/bin/activate
(env) vscode-yara/server$ python3 -m pip install yara-python
```

## Execution
To begin testing, use the `runner.py` script, which will instantiate the event loop and start the server.

Once the server is up and running, open up VSCode and start a Debugging terminal using the `Launch Extension` configuration. Typically, pressing F5 in VSCode will do this all for you.

```sh
(env) vscode-yara$ python3 ./server/runner.py
```

## Logging
The `runner.py` script is configured to print info, error, warning, and critical logs to the screen. Debug logs (mostly raw json-rpc messages) are also written to a `.yara.log` file in the root folder of the repository.

The Python [logging](https://docs.python.org/3/library/logging.html) module is used to control these logs, so feel free to play with it until it works for you.


[logo]: ../images/logo.png "Source Image from blacktop/docker-yara"
