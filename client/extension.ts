"use strict";

import {ChildProcess, spawn} from "child_process";
import {Socket} from "net";
import * as path from "path";
import {platform} from "process";
import {ExtensionContext, OutputChannel, window} from "vscode";
import * as lcp from "vscode-languageclient";
import * as getPort from "get-port";


function install_server(context: ExtensionContext): boolean {
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

function start_server(context: ExtensionContext, lhost: string, tcpPort: number): ChildProcess {
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
    // env/bin/python server.py <lhost> <lport>
    let langserver: ChildProcess = spawn(pythonPath, [serverPath, lhost, tcpPort.toString()], options);
    return langserver;
}

export async function activate(context: ExtensionContext) {
    let outputChannel: OutputChannel = window.createOutputChannel("YARA");
    let lhost: string = "127.0.0.1";
    // grab a random open TCP port to listen to
    let tcpPort: number = await getPort();
    let langserver: ChildProcess = start_server(context, lhost, tcpPort);
    // when the client starts it should open a socket to the server
    const serverOptions: lcp.ServerOptions = function() {
        return new Promise((resolve, reject) => {
            console.log(`Attempting connection to tcp://${lhost}:${tcpPort}`);
            var client = new Socket();
            client.connect(tcpPort, lhost, function() {
                resolve({
                    reader: client,
                    writer: client
                });
            });
        });
    }
    // register the client for all the YARA things
    const clientOptions: lcp.LanguageClientOptions = {
        documentSelector: [{ scheme: "file", language: "yara" }],
        diagnosticCollectionName: "yara",
        outputChannel: outputChannel,
        synchronize: {
            configurationSection: "yara",
        }
    };
    let client = new lcp.LanguageClient(
        "yara-languageclient",
        "YARA",
        serverOptions,
        clientOptions
    );
    client.info("Started YARA extension");
    context.subscriptions.push(client.start());
}

export function deactivate(context: ExtensionContext) {
    // console.log("Deactivating Yara extension");
    context.subscriptions.forEach(disposable => {
        disposable.dispose();
    });
}
