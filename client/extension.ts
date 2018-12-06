"use strict";

import * as path from "path";
import * as vscode from "vscode";
import * as lcp from "vscode-languageclient";


export function activate(context: vscode.ExtensionContext) {
    let serverPath: string = context.asAbsolutePath(path.join("server", "languageServer.py"));
    const serverOptions: lcp.ServerOptions = {
        run: {
            module: serverPath,
            transport: lcp.TransportKind.stdio
        },
        debug: {
            module: serverPath,
            transport: lcp.TransportKind.stdio
        }
    };
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

export function deactivate(context: vscode.ExtensionContext) {
    // console.log("Deactivating Yara extension");
    context.subscriptions.forEach(disposable => {
        disposable.dispose();
    });
}
