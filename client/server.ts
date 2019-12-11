// Functions specifically related to interaction with the language server
"use strict";

import {ChildProcess, spawn} from "child_process";
import * as path from "path";
import {platform} from "process";
import * as tcpPortUsed from "tcp-port-used";
import {ExtensionContext} from "vscode";


export function install_server(context: ExtensionContext): boolean {
    /*
        generate the python runtime & install necessary packages
        returns true or false if installation was successful
    */
    // get the local directory where the env will be installed
    let envPath: string = context.asAbsolutePath(path.join("server", "env"));
    // check if python3.6+ and the "virtualenv" package are installed
    // if not, notify the user and error out
    // else execute the appropriate command to create a Python3 environment
    return false;
}

export async function start_server(context: ExtensionContext, host: string, tcpPort: number): Promise<ChildProcess> {
    /*
        start up the language server with the pre-installed python runtime
        returns the language server's ChildProcess instance
    */
    let serverPath: string = context.asAbsolutePath(path.join("server", "vscode_yara.py"));
    let pythonPath: string = context.asAbsolutePath(path.join("server", "env", "bin", "python"));
    if (platform === "win32") {
        pythonPath = context.asAbsolutePath(path.join("server", "env", "Scripts", "python"));
    }
    // launch the language server
    const options = {
        cwd: context.asAbsolutePath(path.join("server")),
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