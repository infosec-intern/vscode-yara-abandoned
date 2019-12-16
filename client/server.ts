// Functions specifically related to interaction with the language server
"use strict";

import { ChildProcess, spawn } from "child_process";
import * as path from "path";
import { platform } from "process";
import * as tcpPortUsed from "tcp-port-used";


export function install_server(extensionRoot: string): boolean {
    /*
        generate the python runtime & install necessary packages
        returns true or false if installation was successful
    */
    // get the local directory where the env will be installed
    const envPath: string = path.join(extensionRoot, "env");
    // check if python3.6+ is installed

    // if not, notify the user and error out

    // else execute the appropriate command to create a Python3 virtual environment
    // example: python3 -m venv $TEMP/ABC123/env
    let cmd: string = path.join(extensionRoot, "client", "install.sh");
    if (platform == "win32") {
        cmd = path.join(extensionRoot, "client", "install.ps1");
    }
    console.log(`Running command: ${cmd} ${extensionRoot}`);
    let venv_proc: ChildProcess = spawn(cmd, [extensionRoot]);
    venv_proc.on("exit", (code, signal) => {
        // if the process completed successfully
        console.log("install process completed successfully");
        if (code == 0) {
            return true;
        }
    });
    venv_proc.on("error", (error) => {
        console.log(error.message);
        console.log(error);
    });
    return false;
}

export async function start_server(extensionRoot: string, host: string, tcpPort: number): Promise<ChildProcess> {
    /*
        start up the language server with the pre-installed python runtime
        returns the language server's ChildProcess instance
    */
    let serverPath: string = path.join(extensionRoot, "server", "vscode_yara.py");
    let pythonPath: string = path.join(extensionRoot, "server", "env", "bin", "python");
    if (platform === "win32") {
        pythonPath = path.join(extensionRoot, "server", "env", "Scripts", "python");
        // pythonPath = context.asAbsolutePath(path.join("server", "env", "Scripts", "python"));
    }
    // launch the language server
    const options = {
        cwd: path.join(extensionRoot, "server"),
        // cwd: context.asAbsolutePath(path.join("server")),
        detached: false,
        shell: false,
        windowsHide: false
    }
    // env/bin/python server.py <host> <lport>
    let langserver: ChildProcess = spawn(pythonPath, [serverPath, host, tcpPort.toString()], options);
    // wait for the language server to bind to the port
    await tcpPortUsed.waitUntilUsed(tcpPort, host);
    return langserver;
}