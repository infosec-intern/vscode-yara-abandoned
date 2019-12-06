"use strict";

import {ChildProcess, spawn} from "child_process";
import {Socket} from "net";
import * as path from "path";
import {platform} from "process";
import {ExtensionContext, OutputChannel, window} from "vscode";
import * as lcp from "vscode-languageclient";
import * as getPort from "get-port";


export async function activate(context: ExtensionContext) {
    let outputChannel: OutputChannel = window.createOutputChannel("YARA");
    let serverPath: string = context.asAbsolutePath(path.join("server", "vscode_yara.py"));
    let pythonPath: string = context.asAbsolutePath(path.join("server", "env", "bin", "python"));
    if (platform === "win32") {
        pythonPath = context.asAbsolutePath(path.join("server", "env", "Scripts", "python"));
    }
    let lhost: string = "127.0.0.1";
    // grab a random open TCP port to listen to
    let tcpPort: number = await getPort();
    // launch the language server
    const options = {
        cwd: context.asAbsolutePath(path.join("server")),
        detached: false,
        shell: false,
        windowsHide: false
    }
    // env/bin/python script.py <lhost> <lport>
    let langserver: lcp.Executable = {
        command: pythonPath,
        args: [serverPath, lhost, tcpPort.toString()],
        options: options
    };
    const serverOptions: lcp.ServerOptions = {
        run: langserver,
        debug: langserver
    };
    const clientOptions: lcp.LanguageClientOptions = {
        documentSelector: [{ scheme: "file", language: "yara" }],
        diagnosticCollectionName: "yara",
        outputChannel: outputChannel,
    };
    let client = new lcp.LanguageClient(
        "yara-languageclient",
        "YARA",
        serverOptions,
        clientOptions
    );
    client.info("Connected to YARA Language Server");
    context.subscriptions.push(client.start());
}

export function deactivate(context: ExtensionContext) {
    // console.log("Deactivating Yara extension");
    context.subscriptions.forEach(disposable => {
        disposable.dispose();
    });
}
