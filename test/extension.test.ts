"use strict";

import * as assert from "assert";
import { ChildProcess } from "child_process";
import * as fs from "fs";
import { createConnection, Socket } from "net";
import * as path from "path";
import * as vscode from "vscode";
import { install_server, start_server, server_installed } from "../client/server";

const ext_id: string = "infosec-intern.yara";
const workspace: string = path.join(__dirname, "..", "..", "test/rules/");


// lazily pulled from https://solvit.io/53b9763
const removeDir = function(dirPath: string) {
    const fs = require("fs");
    const path = require("path");
    if (fs.existsSync(dirPath)) {
        return;
    }
    let list = fs.readdirSync(dirPath);
    for (let i = 0; i < list.length; i++) {
        let filename = path.join(dirPath, list[i]);
        let stat = fs.statSync(filename);
        if (filename == "." || filename == "..") {
            // do nothing for current and parent dir
        } else if (stat.isDirectory()) {
            removeDir(filename);
        } else {
            fs.unlinkSync(filename);
        }
    }
    fs.rmdirSync(dirPath);
};

// Unit tests to ensure the setup functions are working appropriately
suite("YARA: Setup", function () {
    /*
        give this test a generous timeout of 10 seconds to ensure the install
        has enough time to finish before the test is killed
    */
    test("install server", function (done) {
        // ensure the server components are installed if none exist
        const fs = require("fs");
        const os = require("os");
        const extensionRoot: string = path.join(__dirname, "..", "..");
        const targetDir: string = fs.mkdtempSync(`${os.tmpdir()}${path.sep}`);
        const installResult: boolean = install_server(extensionRoot, targetDir);
        // install_server creates the env/ directory when successful
        let dirExists: boolean = fs.existsSync(path.join(targetDir, "env"));
        try {
            removeDir(targetDir);
        } catch {
            console.log(`Couldn't remove temporary directory "${targetDir}". Manual removal required`);
        }
        assert(installResult && dirExists);
        done();
    }).timeout(10000);
    /*
        Have to report this test as complete in a slightly different way
        due to the "async" requirement
        see: https://github.com/mochajs/mocha/issues/2407
    */
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
    test("server installed", function (done) {
        const fs = require("fs");
        const os = require("os");
        const extensionRoot: string = path.join(__dirname, "..", "..");
        const targetDir: string = fs.mkdtempSync(`${os.tmpdir()}${path.sep}`);
        install_server(extensionRoot, targetDir);
        assert(server_installed(targetDir));
        done();
    }).timeout(10000);
});

// Integration tests to ensure the client is working independently of the server
suite("YARA: Client", function () {
    test("client connection refused", function (done) {
        // ensure the client throws an error message if the connection is refused and the server is shut down
        const filepath: string = path.join(workspace, "peek_rules.yara");
        let extension = vscode.extensions.getExtension(ext_id);
        extension.activate().then((api) => {
            // kill the server process, then try to open the client against it
            api.get_server().process.kill();
            vscode.workspace.openTextDocument(filepath).then(function (doc) {
                console.log(`${extension.id} is active? ${extension.isActive}`);
            });
        });
    });
    test("start server", async function (done) {
        // ensure the language server is started as the client's child process
        // by checking that the PID exists
        /*
        let extension = vscode.extensions.getExtension(ext_id);
        extension.activate().then((api) => {
            let server_proc: ChildProcess = api.get_server().process;
            assert(server_proc.pid > -1);
            done();
        });
        */
       /*
        let ws: vscode.Uri = vscode.Uri.file(workspace);
        let thing = await vscode.commands.executeCommand("vscode.openFolder", ws, {newWindow: true});
        console.log(thing);
        */
    });
    test("stop server", function (done) {
        // ensure the language server is stopped if the client ends
        const filepath: string = path.join(workspace, "peek_rules.yara");
        vscode.workspace.openTextDocument(filepath).then(function (doc) {});
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
    test("code completion", function (done) {
        const filepath: string = path.join(workspace, "code_completion.yara");
        vscode.workspace.openTextDocument(filepath).then(async function (doc) {
            let uri: vscode.Uri = vscode.Uri.file(filepath);
            let pos: vscode.Position = new vscode.Position(9, 16);
            vscode.commands.executeCommand("vscode.executeCompletionItemProvider", uri, pos, "\.").then((items) => {
                console.log("completion provider complete");
                console.log(items);
            });
        });
    });
    test.skip("command CompileRule", function(done) {
        // should compile the active document in the current texteditor
        const cmd: string = "yara.CompileRule";
        vscode.commands.getCommands(true).then((cmds) => {
            assert(cmds.indexOf(cmd) != -1);
        });
        vscode.commands.executeCommand(cmd).then((items) => {
            console.log(`Executed command: ${cmd}`);
            console.log(items);
        });
    });
    test.skip("command CompileAllRules with workspace", function(done) {
        // should compile all .yar and .yara rules in the current workspace
        const cmd: string = "yara.CompileAllRules";
        vscode.commands.getCommands(true).then((cmds) => {
            assert(cmds.indexOf(cmd) != -1);
        });
        vscode.commands.executeCommand(cmd).then((items) => {
            console.log(`Executed command: ${cmd}`);
            console.log(items);
        });
    });
    test.skip("command CompileAllRules without workspace", function(done) {
        // should compile all dirty files in the current texteditor
        const cmd: string = "yara.CompileAllRules";
        vscode.commands.getCommands(true).then((cmds) => {
            assert(cmds.indexOf(cmd) != -1);
        });
        vscode.commands.executeCommand(cmd).then((items) => {
            console.log(`Executed command: ${cmd}`);
            console.log(items);
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
