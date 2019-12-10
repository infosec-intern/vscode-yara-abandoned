"use strict";

import * as path from "path";
import * as vscode from "vscode";
import { ChildProcess } from "child_process";
import { createConnection, Socket } from "net";

let ext_id: string = "infosec-intern.yara";
let workspace: string = path.join(__dirname, "..", "..", "test/rules/");


// Integration tests to ensure the client is working independently of the server
suite("YARA: Client", function () {
    test.skip("client connection refused", function (done) {
        // ensure the client throws an error message if the connection is refused and the server is shut down
    });
    test.skip("install server", function (done) {
        // ensure the server components are installed if none exist
    });
    test("server binding", function (done) {
        // ensure the server binds to a port so the client can connect
        let extension = vscode.extensions.getExtension(ext_id);
        extension.activate().then((api) => {
            let server = api.get_server();
            // connect to the server with a dummy listener
            let connection: Socket = createConnection(server.port, server.host, () => {});
            // and resolve if it was successful
            connection.on("connect", () => { done(); });
        });
    });
    test("start server", function (done) {
        // ensure the language server is started as a child process
        // by checking that the PID exists
        let extension = vscode.extensions.getExtension(ext_id);
        extension.activate().then((api) => {
            let server_proc: ChildProcess = api.get_server().process;
            if (server_proc.pid > -1) { done(); }
        });
    });
    test.skip("stop server", function (done) {
        // ensure the language server is stopped if the client ends
    });
});

// Integration tests to ensure the client and server are interacting as expected
suite("YARA: Language Server", function () {
    test.skip("rule definition", function (done) {
        const filepath: string = path.join(workspace, "peek_rules.yara");
        vscode.workspace.openTextDocument(filepath).then(function (doc) {

        });
    });

    test.skip("variable definition", function (done) {
        const filepath: string = path.join(workspace, "peek_rules.yara");
        vscode.workspace.openTextDocument(filepath).then(function (doc) {

        });
    });

    test.skip("symbol references", function (done) {
        const filepath: string = path.join(workspace, "peek_rules.yara");
        vscode.workspace.openTextDocument(filepath).then(function (doc) {

        });
    });

    test.skip("wildcard references", function (done) {
        const filepath: string = path.join(workspace, "peek_rules.yara");
        vscode.workspace.openTextDocument(filepath).then(function (doc) {

        });
    });

    test.skip("code completion", function (done) {
        const filepath: string = path.join(workspace, "code_completion.yara");
        vscode.workspace.openTextDocument(filepath).then(function (doc) {

        });
    });

    /*
        Trying to capture $hex_string but not $hex_string2
        Should collect references for:
            $hex_string = { E2 34 ?? C8 A? FB [2-4] }
            $hex_string
        But not:
            $hex_string2 = { F4 23 ( 62 B4 | 56 ) 45 }
    */
    test.skip("issue #17", function (done) {
        const filepath: string = path.join(workspace, "peek_rules.yara");
        vscode.workspace.openTextDocument(filepath).then(function (doc) {

        });
    });
});
