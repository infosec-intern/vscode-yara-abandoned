"use strict";

import {Socket} from "net";
import * as path from "path";
import {ExtensionContext, OutputChannel, window} from "vscode";
import * as lcp from "vscode-languageclient";


export function activate(context: ExtensionContext) {
    let serverPath: string = context.asAbsolutePath(path.join("server", "runner.py"));
    let pythonPath: string = context.asAbsolutePath(path.join("server", "env", "Scripts", "python"));
    let outputChannel: OutputChannel = window.createOutputChannel("YARA");
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
