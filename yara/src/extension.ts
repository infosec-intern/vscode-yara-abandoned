"use strict";

import * as path from "path";
import { workspace, ExtensionContext } from "vscode";

import * as lcp from "vscode-languageclient";

let client: lcp.LanguageClient;

export function activate(context: ExtensionContext) {
    let serverModule: string = context.asAbsolutePath(path.join("yara", "src", "languageServer.py"));
    let serverOptions: lcp.ServerOptions = {
        run: {
            module: serverModule,
            transport: lcp.TransportKind.ipc
        },
        debug: {
            module: serverModule,
            transport: lcp.TransportKind.ipc
        }
    };
    let clientOptions: lcp.LanguageClientOptions = {
        documentSelector: [{ scheme: "file", language: "yara" }]
    };
    client = new lcp.LanguageClient("yara", "Yara", serverOptions, clientOptions);
    client.start();
}

export function deactivate(): Thenable<void> {
    if (!client) {
        return undefined;
    }
    return client.stop();
}
