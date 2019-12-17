// Functions specifically related to interaction with the language server
"use strict";

import { ChildProcess, spawn, spawnSync } from "child_process";
import * as path from "path";
import { platform } from "process";
import * as tcpPortUsed from "tcp-port-used";


export function install_server(extensionRoot: string, targetDir: string): boolean {
    /*
        generate the python runtime & install necessary packages
        returns true or false if installation was successful
    */
    // get the local directory where the env will be installed
    let cmd: string = path.join(extensionRoot, "client", "install.sh");
    let args: string[] = [targetDir];
    if (platform == "win32") {
        // suspicious AF
        cmd = "powershell.exe";
        args = [
            path.join(extensionRoot, "client", "install.ps1"),
            targetDir
        ];
    }
    // we should be generating all command and arguments ourself
    // so shell: true *should* be safe
    // TODO: verify that assumption
    let venv_proc = spawnSync(cmd, args, {shell: true});
    return venv_proc.status == 0;
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