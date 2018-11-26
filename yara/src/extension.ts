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
        // Register the server for yara documents
        documentSelector: [{ scheme: "file", language: "yara" }],
        synchronize: {
            // Notify the server about file changes to .yara files contained in the workspace
            fileEvents: workspace.createFileSystemWatcher("**/.yara")
        }
    };

    // Create the language client and start the client.
    client = new lcp.LanguageClient(
        "yara",
        "Yara",
        serverOptions,
        clientOptions
    );

    // Start the client. This will also launch the server
    client.start();
}

export function deactivate(): Thenable<void> {
    if (!client) {
        return undefined;
    }
    return client.stop();
}
