"use strict";

import * as assert from "assert";
import { ChildProcess } from "child_process";
import { createConnection, Socket } from "net";
import * as path from "path";
import * as vscode from "vscode";
import { install_server, start_server } from "../client/server";

let ext_id: string = "infosec-intern.yara";
let workspace: string = path.join(__dirname, "..", "..", "test/rules/");


// Unit tests to ensure the setup functions are working appropriately
suite("YARA: Setup", function () {
    /*
        Have to report these tests as complete in a slightly different way
        due to the "async" requirement
        see: https://github.com/mochajs/mocha/issues/2407
    */
    test("install server", function (done) {
        // ensure the server components are installed if none exist
        const fs = require("fs");
        const os = require("os");
        const { ENOENT } = require("constants");
        const folder: string = fs.mkdtempSync(`${os.tmpdir()}${path.sep}`);
        const installResult: boolean = install_server(folder);
        // install_server creates the env/ directory when successful
        let dirExists: boolean = false;
        try {
            dirExists = fs.existsSync(path.join(folder, "env"));
            console.log(`dirExists: ${dirExists}`);
        } catch (error) {
            console.log(`error: ${error.message}`);
        }
        fs.rmdirSync(folder);
        assert(installResult && dirExists);
    });
    test("server binding", async function () {
        // ensure the server binds to a port so the client can connect
        const host: string = "127.0.0.1";
        const port: number = 8471;
        const extensionRoot: string = path.join(__dirname, "..", "..");
        await start_server(extensionRoot, host, port);
        return new Promise((resolve, reject) => {
            let connection: Socket = createConnection(port, host, () => {});
            connection.on("connect", () => {
                connection.end();
                resolve();
            });
        });
    });
});

// Integration tests to ensure the client is working independently of the server
suite("YARA: Client", function () {
    test.skip("client activation", function (done) {
        // ensure the client properly activates this extension when given a YARA file
        const filepath: string = path.join(workspace, "peek_rules.yara");
        vscode.workspace.openTextDocument(filepath).then(function (doc) {
            let extension = vscode.extensions.getExtension(ext_id);
            assert(extension.isActive);
            done();
        });
    });
    test("client connection refused", function (done) {
        // ensure the client throws an error message if the connection is refused and the server is shut down
    });
    test("install on first exec", function (done) {
        // ensure the server is installed if conditions are met
    });
    test("start server", function (done) {
        // ensure the language server is started as the client's child process
        // by checking that the PID exists
        let extension = vscode.extensions.getExtension(ext_id);
        extension.activate().then((api) => {
            let server_proc: ChildProcess = api.get_server().process;
            assert(server_proc.pid > -1);
            done();
        });
    });
    test("stop server", function (done) {
        // ensure the language server is stopped if the client ends
        const filepath: string = path.join(workspace, "peek_rules.yara");
        vscode.workspace.openTextDocument(filepath).then(function (doc) {});
    });
});

// Integration tests to ensure the client and server are interacting as expected
suite("YARA: Language Server", function () {
    test("rule definition", function (done) {
        const filepath: string = path.join(workspace, "peek_rules.yara");
        vscode.workspace.openTextDocument(filepath).then(function (doc) {

        });
    });
    test("variable definition", function (done) {
        const filepath: string = path.join(workspace, "peek_rules.yara");
        vscode.workspace.openTextDocument(filepath).then(function (doc) {

        });
    });
    test("symbol references", function (done) {
        const filepath: string = path.join(workspace, "peek_rules.yara");
        vscode.workspace.openTextDocument(filepath).then(function (doc) {

        });
    });
    test("wildcard references", function (done) {
        const filepath: string = path.join(workspace, "peek_rules.yara");
        vscode.workspace.openTextDocument(filepath).then(function (doc) {

        });
    });
    test("code completion", function (done) {
        const filepath: string = path.join(workspace, "code_completion.yara");
        vscode.workspace.openTextDocument(filepath).then(function (doc) {

        });
    });
    test("command CompileRule", function(done) {

    });
    test("command CompileAllRules", function(done) {

    });
    /*
        Trying to capture $hex_string but not $hex_string2
        Should collect references for:
            $hex_string = { E2 34 ?? C8 A? FB [2-4] }
            $hex_string
        But not:
            $hex_string2 = { F4 23 ( 62 B4 | 56 ) 45 }
    */
    test("issue #17", function (done) {
        const filepath: string = path.join(workspace, "peek_rules.yara");
        vscode.workspace.openTextDocument(filepath).then(function (doc) {

        });
    });
});
