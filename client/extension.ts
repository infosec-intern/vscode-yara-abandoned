"use strict";

import * as path from "path";
import * as vscode from "vscode";

import * as lcp from "vscode-languageclient";

let client: lcp.LanguageClient;

export function activate(context: vscode.ExtensionContext) {
    // let envPath: string = context.asAbsolutePath(path.join("..", "..", "server", "env"))
    let serverModule: string = context.asAbsolutePath(path.join("server", "languageServer.py"));
    let serverOptions: lcp.ServerOptions = {
        run: {
            module: serverModule,
            transport: lcp.TransportKind.socket
        },
        debug: {
            module: serverModule,
            transport: lcp.TransportKind.socket
        }
    };
    let clientOptions: lcp.LanguageClientOptions = {
        documentSelector: [{ scheme: "file", language: "yara" }],
        diagnosticCollectionName: "yara",
        stdioEncoding: "utf8"
    };
    client = new lcp.LanguageClient("yara","Yara",serverOptions,clientOptions);
    client.start();
}

export function deactivate(): Thenable<void> {
    if (!client) {
        return undefined;
    }
    return client.stop();
}
