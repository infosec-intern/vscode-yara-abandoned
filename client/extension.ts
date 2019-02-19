"use strict";

import {ChildProcess, spawn} from "child_process";
import {Socket} from "net";
import * as path from "path";
import {platform} from "process";
import {ExtensionContext, OutputChannel, window} from "vscode";
import * as lcp from "vscode-languageclient";


export function activate(context: ExtensionContext) {
    let outputChannel: OutputChannel = window.createOutputChannel("YARA");
    let serverPath: string = context.asAbsolutePath(path.join("server", "runner.py"));
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
    let langserver: ChildProcess = spawn(pythonPath, [serverPath], options);
    // launch the client
    const serverOptions: lcp.ServerOptions = function() {
		return new Promise((resolve, reject) => {
            var client = new Socket();
			client.connect(8471, "127.0.0.1", function() {
                console.log(`client connected to ${client.localAddress}:${client.localPort}`);
				resolve({
					reader: client,
					writer: client
				});
			});
		});
    }
    langserver.stdout.on('data', (data) => {
        console.log(`stdout: ${data}`);
    });

    langserver.stderr.on('data', (data) => {
        console.log(`stderr: ${data}`);
    });

    langserver.on('close', (code) => {
        console.log(`child process exited with code ${code}`);
    });
    // let debugOptions = { execArgv: ["--nolazy"] };
    // const serverOptions: lcp.ServerOptions = {
    //     run: {
    //         module: `${pythonPath} ${serverPath}`,
    //         transport: lcp.TransportKind.ipc
    //     },
    //     debug: {
    //         module: `${pythonPath} ${serverPath}`,
    //         transport: lcp.TransportKind.ipc,
    //         options: debugOptions
    //     }
    // }
    const clientOptions: lcp.LanguageClientOptions = {
        documentSelector: [{ scheme: "file", language: "yara" }],
        diagnosticCollectionName: "yara",
        outputChannel: outputChannel,
        synchronize: { configurationSection: "yara" }
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
