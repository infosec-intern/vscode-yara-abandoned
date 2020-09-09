// Functions specifically related to interaction with the language server
"use strict";

import { ChildProcess, spawn, spawnSync } from "child_process";
import { existsSync } from "fs";
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
    // console.log(`Installing server with command: ${cmd} ${args.join(" ")}`);
    // we should be generating all command and arguments ourself
    // so shell: true *should* be safe
    // TODO: verify that assumption
    let venv_proc = spawnSync(cmd, args, {shell: true});
    return venv_proc.status == 0;
}

export async function start_server(serverRoot: string, host: string, tcpPort: number): Promise<ChildProcess> {
    /*
        start up the language server with the pre-installed python runtime
        returns the language server's ChildProcess instance
    */
    let serverPath: string = path.join(serverRoot, "env", "bin", "vscode_yara.py");
    let pythonPath: string = path.join(serverRoot, "env", "bin", "python");
    if (platform === "win32") {
        serverPath = path.join(serverRoot, "env", "Scripts", "vscode_yara.py");
        pythonPath = path.join(serverRoot, "env", "Scripts", "python");
    }
    // launch the language server
    const options = {
        cwd: serverRoot,
        detached: false,
        shell: false,
        windowsHide: false
    }
    // env/bin/python server.py <host> <lport>
    let langserver: ChildProcess = spawn(pythonPath, [serverPath, host, tcpPort.toString()], options);
    // wait for the language server to bind to the port
    await tcpPortUsed.waitUntilUsed(tcpPort, host);
    // console.log(`Running language server with the following cli: ${serverPath} ${host} ${tcpPort}`);
    return langserver;
}

export function server_installed(installDir: string): boolean {
    let envPath: string = path.join(installDir, "env");
    if (!existsSync(envPath)) {
        return false;
    }
    // console.log(`Venv found in ${envPath}`);
    let cmd: string = path.join(envPath, "bin", "pip");
    let args: string[] = ["freeze"];
    if (platform == "win32") {
        // suspicious AF
        cmd = "powershell.exe";
        args = [
            path.join(envPath, "Scripts", "pip.exe"),
            "freeze"
        ];
    }
    const pip_proc = spawnSync(cmd, args, {shell: true});
    return pip_proc.stdout.toString().includes("yarals");
}
