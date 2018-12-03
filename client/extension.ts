"use strict";

import * as path from "path";
import * as vscode from "vscode";
import * as lcp from "vscode-languageclient";


// https://github.com/palantir/python-language-server/blob/develop/vscode-client/src/extension.ts
function startLanguageServer(command: string, args: Array<string>): vscode.Disposable {
    const serverOptions: lcp.ServerOptions = { command, args };
    const clientOptions: lcp.LanguageClientOptions = {
        documentSelector: [{ scheme: "file", language: "yara" }],
        diagnosticCollectionName: "yara",
        stdioEncoding: "utf8",
        synchronize: { configurationSection: "yara" }
    };
    return new lcp.LanguageClient(command, serverOptions, clientOptions).start();
}

export function activate(context: vscode.ExtensionContext) {
    let serverPath: string = context.asAbsolutePath(path.join("server", "languageServer.py"));
    let client = startLanguageServer(serverPath, []);
    context.subscriptions.push(client);
}

export function deactivate(context: vscode.ExtensionContext) {
    // console.log("Deactivating Yara extension");
    context.subscriptions.forEach(disposable => {
        disposable.dispose();
    });
}
