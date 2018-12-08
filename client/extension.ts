"use strict";

import {execSync} from "child_process";
import {Socket} from "net";
import * as path from "path";
import {ExtensionContext} from "vscode";
import * as lcp from "vscode-languageclient";


export function activate(context: ExtensionContext) {
    let serverPath: string = context.asAbsolutePath(path.join("server", "languageServer.py"));
    let pythonPath: string = context.asAbsolutePath(path.join("server", "env", "Scripts", "python"));
    const serverOptions: lcp.ServerOptions = function() {
        // execSync(`${pythonPath} ${serverPath}`);
		return new Promise((resolve, reject) => {
            var client = new Socket();
            console.log("created socket");
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
        stdioEncoding: "utf8",
        synchronize: { configurationSection: "yara" }
    };
    let client = new lcp.LanguageClient(
        "yara-languageclient",
        "YARA",
        serverOptions,
        clientOptions
    );
    client.info("test info log");
    client.error("test error log");
    client.warn("test warn log");
    context.subscriptions.push(client.start());
}

export function deactivate(context: ExtensionContext) {
    // console.log("Deactivating Yara extension");
    context.subscriptions.forEach(disposable => {
        disposable.dispose();
    });
}
