"use strict";

import {ChildProcess, spawn} from "child_process";
import {Socket} from "net";
import * as path from "path";
import {platform} from "process";
import {Disposable, ExtensionContext, OutputChannel, window} from "vscode";
import * as lcp from "vscode-languageclient";
import * as getPort from "get-port";
import * as tcpPortUsed from "tcp-port-used";


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

async function start_server(context: ExtensionContext, host: string, tcpPort: number): Promise<ChildProcess> {
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

export async function activate(context: ExtensionContext) {
    let outputChannel: OutputChannel = window.createOutputChannel("YARA");
    let lhost: string = "127.0.0.1";
    // grab a random open TCP port to listen to
    let tcpPort: number = await getPort();
    let langserver: ChildProcess = await start_server(context, lhost, tcpPort);
    console.log(`Language Server started with PID: ${langserver.pid}`);
    // when the client starts it should open a socket to the server
    const serverOptions: lcp.ServerOptions = function() {
        return new Promise((resolve, reject) => {
            console.log(`Attempting connection to tcp://${lhost}:${tcpPort}`);
            let connection: Socket = new Socket({readable: true, writable: true});
            connection.connect(tcpPort, lhost, function() {
                resolve({
                    reader: connection,
                    writer: connection
                });
            });
            connection.on("error", (error) => {
                // apparently net.Socket just rewraps errors as a generic Error object
                // kind of annoying, but workable
                if (error.message.includes("ECONNREFUSED")) {
                    let msg: string = "Could not connect to YARA Language Server. Is it running?"
                    window.showErrorMessage(msg);
                    window.setStatusBarMessage(`Not connected to YARA Language Server`);
                }
                else {
                    let msg: string = `YARA: ${error.message}`;
                    window.showErrorMessage(msg);
                }
            });
        });
    }
    // register the client for all the YARA things
    const clientOptions: lcp.LanguageClientOptions = {
        documentSelector: [{language: "yara"}],
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
    // kill the server's process when disposing of it
    context.subscriptions.push(new Disposable(langserver.kill));
}

export function deactivate(context: ExtensionContext) {
    // console.log("Deactivating Yara extension");
    context.subscriptions.forEach(disposable => {
        disposable.dispose();
    });
}
