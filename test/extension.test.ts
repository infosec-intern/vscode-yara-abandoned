"use strict";

import * as assert from "assert";
import { ChildProcess } from "child_process";
import { createConnection, Socket } from "net";
import * as fs from "fs";
import * as path from "path";
import * as os from "os";
import * as vscode from "vscode";
import * as lcp from "vscode-languageclient";
import { install_server, start_server, server_installed } from "../client/server";

const ext_id: string = "infosec-intern.yara";
const workspace: string = path.join(__dirname, "..", "..", "test/rules/");

// lazily pulled from https://solvit.io/53b9763
const removeDir = function(dirPath: string) {
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
    // this.timeout(10000);
    const extensionRoot: string = path.join(__dirname, "..", "..");
    let targetDir: string = "";

    setup(function () {
        // ensure the server components are installed if none exist
        targetDir = fs.mkdtempSync(`${os.tmpdir()}${path.sep}`);
    });
    teardown(function () {
        try {
            removeDir(targetDir);
        } catch (err) {
            console.log(`Couldn't remove targetDir: ${err}`);
        }
    });
    test("install server", function (done) {
        const installResult: boolean = install_server(extensionRoot, targetDir);
        // install_server creates the env/ directory when successful
        let dirExists: boolean = fs.existsSync(path.join(targetDir, "env"));
        console.log(`installResult && dirExists: ${installResult} && ${dirExists}`);
        assert.equal(true, (installResult && dirExists));
        done();
    });
    /*
        Have to report this test as complete in a slightly different way
        due to the "async" requirement
        see: https://github.com/mochajs/mocha/issues/2407
    */
    test("server binding", async function () {
        // ensure the server binds to a port so the client can connect
        const host: string = "127.0.0.1";
        const port: number = 8471;
        install_server(extensionRoot, targetDir);
        await start_server(targetDir, host, port);
        return new Promise(function (resolve, reject) {
            const connection: Socket = createConnection(port, host, function () {
                connection.end();
                resolve();
            });
        });
    });
    test("server installed", function (done) {
        install_server(extensionRoot, targetDir);
        assert.equal(true, server_installed(targetDir));
        done();
    });
});

// Integration tests to ensure the client is working independently of the server
suite("YARA: Client", function () {
    // this.timeout(5000);
    let extension: vscode.Extension<any>|null = null;

    setup(function () {
        extension = vscode.extensions.getExtension(ext_id);
    });
    test.skip("client connection refused", async function () {
        // ensure the client throws an error message if the connection is refused and the server is shut down
        const filepath: string = path.join(workspace, "peek_rules.yara");
        const uri: vscode.Uri = vscode.Uri.file(filepath);
        const pos: vscode.Position = new vscode.Position(42, 14);
        // kill the server process, then try to open the client against it
        const api = await extension.activate();
        api.get_server().process.kill();
        let results: Array<vscode.Location> = await vscode.commands.executeCommand("vscode.executeDefinitionProvider", uri, pos);
        assert(results.length == 0);
        // TODO: assert(messagethrown)
        // TODO: assert(statusbarchanged)
    });
    test("start server", async function () {
        // ensure the language server is started as the client's child process
        // by checking that the PID exists
        let api = await extension.activate();
        let server_proc: ChildProcess = api.get_server().process;
        assert(server_proc.pid > -1);
    });
    test.skip("stop server", async function () {
        // ensure the language server is stopped if the client ends
        const filepath: string = path.join(workspace, "peek_rules.yara");
        let doc: vscode.TextDocument = await vscode.workspace.openTextDocument(filepath);
    });
});

// Integration tests to ensure the client and server are interacting as expected
suite.skip("YARA: Language Server", function () {
    // this.timeout(5000);

    suiteSetup(async function () {
        let extension = vscode.extensions.getExtension(ext_id);
        await extension.activate();
    });
    test("rule definition", async function () {
        const filepath: string = path.join(workspace, "peek_rules.yara");
        const uri: vscode.Uri = vscode.Uri.file(filepath);
        // SyntaxExample: Line 43, Col 14
        const expectedSymbol: string = "SyntaxExample";
        const pos: vscode.Position = new vscode.Position(42, 14);
        let doc: vscode.TextDocument = await vscode.workspace.openTextDocument(filepath);
        let results: Array<vscode.Location> = await vscode.commands.executeCommand("vscode.executeDefinitionProvider", uri, pos);
        assert(results.length == 1, `Wrong number of definitions. ${results.length} instead of 1`);
        let result: vscode.Location = results[0];
        assert(result.uri.path == uri.path, `Incorrect document searched: ${result.uri.path} searched instead of ${filepath}`);
        let refWordRange: vscode.Range|undefined = doc.getWordRangeAtPosition(result.range.start);
        let refWord: string = doc.getText(refWordRange);
        assert(refWord == expectedSymbol, `${refWord} does not match ${expectedSymbol}`);
    });
    test("variable definition", async function () {
        const filepath: string = path.join(workspace, "peek_rules.yara");
        const uri: vscode.Uri = vscode.Uri.file(filepath);
        // $hex_string: Line 25, Col 14
        const expectedSymbol: string = "hex_string";
        const pos: vscode.Position = new vscode.Position(24, 14);
        let doc: vscode.TextDocument = await vscode.workspace.openTextDocument(filepath);
        let results: Array<vscode.Location> = await vscode.commands.executeCommand("vscode.executeDefinitionProvider", uri, pos);
        assert(results.length == 1, `Wrong number of definitions. ${results.length} instead of 1`);
        let result: vscode.Location = results[0];
        assert(result.uri.path == uri.path, `Incorrect document searched: ${result.uri.path} searched instead of ${filepath}`);
        let refWordRange: vscode.Range|undefined = doc.getWordRangeAtPosition(result.range.start);
        let refWord: string = doc.getText(refWordRange);
        assert(refWord == expectedSymbol, `"${refWord}" does not match ${expectedSymbol}`);
    });
    test("symbol references", async function () {
        const filepath: string = path.join(workspace, "peek_rules.yara");
        const uri: vscode.Uri = vscode.Uri.file(filepath);
        // $dstring: Line 22, Col 11
        const expectedSymbol: string = "dstring";
        const pos: vscode.Position = new vscode.Position(21, 11);
        const acceptableLines: Set<number> = new Set([21, 28, 29]);
        let doc: vscode.TextDocument = await vscode.workspace.openTextDocument(filepath);
        let results: Array<vscode.Location> = await vscode.commands.executeCommand("vscode.executeReferenceProvider", uri, pos);
        assert(results.length == 3, `Wrong number of reference items. ${results.length} instead of 3`);
        results.forEach(reference => {
            assert(reference.uri.path == uri.path, `Incorrect document searched: ${reference.uri.path} searched instead of ${filepath}`);
            let refWordRange: vscode.Range = doc.getWordRangeAtPosition(reference.range.start);
            let refWord: string = doc.getText(refWordRange);
            assert(refWord == expectedSymbol, `"${refWord}" does not match ${expectedSymbol}`);
            assert(acceptableLines.has(reference.range.start.line), `${reference.range.start.line} is not in the list of acceptable lines`);
        });
    });
    test("wildcard references", async function () {
        const filepath: string = path.join(workspace, "peek_rules.yara");
        const uri: vscode.Uri = vscode.Uri.file(filepath);
        // ($hex_*): Line 31, Col 11
        const expectedSymbol: string = "hex_";
        const pos: vscode.Position = new vscode.Position(30, 11);
        const acceptableLines: Set<number> = new Set([19, 20]);
        let doc: vscode.TextDocument = await vscode.workspace.openTextDocument(filepath);
        let results: Array<vscode.Location> = await vscode.commands.executeCommand("vscode.executeReferenceProvider", uri, pos);
        assert(results.length == 2, `Wrong number of reference items. ${results.length} instead of 2`);
        results.forEach(reference => {
            assert(reference.uri.path == uri.path, `Incorrect document searched: ${reference.uri.path} searched instead of ${filepath}`);
            let refWordRange: vscode.Range = doc.getWordRangeAtPosition(reference.range.start);
            let refWord: string = doc.getText(refWordRange);
            assert(refWord.startsWith(expectedSymbol), `"${refWord}" does not match the wildcard expression "${expectedSymbol}*"`);
            assert(acceptableLines.has(reference.range.start.line), `${reference.range.start.line} is not in the list of acceptable lines`);
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
    test("similar symbol references", async function () {
        const filepath: string = path.join(workspace, "peek_rules.yara");
        const uri: vscode.Uri = vscode.Uri.file(filepath);
        // $hex_string: Line 20, Col 11
        const expectedSymbol: string = "hex_";
        const pos: vscode.Position = new vscode.Position(19, 11);
        const acceptableLines: Set<number> = new Set([19, 24]);
        let doc: vscode.TextDocument = await vscode.workspace.openTextDocument(filepath);
        let results: Array<vscode.Location> = await vscode.commands.executeCommand("vscode.executeReferenceProvider", uri, pos);
        assert(results.length == 2, `Wrong number of reference items. ${results.length} instead of 2`);
        results.forEach(reference => {
            assert(reference.uri.path == uri.path, `Incorrect document searched: ${reference.uri.path} searched instead of ${filepath}`);
            let refWordRange: vscode.Range = doc.getWordRangeAtPosition(reference.range.start);
            let refWord: string = doc.getText(refWordRange);
            assert(refWord.startsWith(expectedSymbol), `"${refWord}" does not match the wildcard expression "${expectedSymbol}*"`);
            assert(acceptableLines.has(reference.range.start.line), `${reference.range.start.line} is not in the list of acceptable lines`);
        });
    });
    test("hover", async function () {
        const filepath: string = path.join(workspace, "peek_rules.yara");
        const uri: vscode.Uri = vscode.Uri.file(filepath);
        // @dstring[1]: Line 30, Col 12
        // $dstring = "double string" wide nocase fullword
        const expectedValue: string = "\"double string\" wide nocase fullword";
        const pos: vscode.Position = new vscode.Position(29, 12);
        let results: Array<lcp.Hover> = await vscode.commands.executeCommand("vscode.executeHoverProvider", uri, pos);
        assert(results.length == 1);
        let markup: lcp.MarkupContent = results[0].contents[0];
        assert(markup.value == expectedValue);
    });
    test("code completion", async function () {
        const filepath: string = path.join(workspace, "code_completion.yara");
        const uri: vscode.Uri = vscode.Uri.file(filepath);
        // cuckoo: Line 10, Col 15
        const pos: vscode.Position = new vscode.Position(9, 15);
        const acceptableTerms: Set<string> = new Set(["filesystem", "network", "registry", "sync"]);
        let results: vscode.CompletionList = await vscode.commands.executeCommand("vscode.executeCompletionItemProvider", uri, pos);
        assert(results.items.length == 4, `Wrong number of completion items. ${results.items.length} instead of 4`);
        assert(results.isIncomplete == false, "Completion list reported as incomplete");
        results.items.forEach((item: vscode.CompletionItem) => {
            assert(item.kind == vscode.CompletionItemKind.Class, `"${item.kind.toString()}" is not a valid completion item type for this set`);
            assert(acceptableTerms.has(item.label), `"${item.label}" is not a valid completion label for this set`);
        });
    });
    test("renames", async function () {
        const filepath: string = path.join(workspace, "peek_rules.yara");
        const uri: vscode.Uri = vscode.Uri.file(filepath);
        // $dstring: Line 22, Col 13
        const pos: vscode.Position = new vscode.Position(21, 13);
        const newName: string = "renamed";
        const acceptableLines: Set<number> = new Set([21, 28, 29]);
        let results: vscode.WorkspaceEdit = await vscode.commands.executeCommand("vscode.executeDocumentRenameProvider", uri, pos, newName);
        assert(results.get(uri).length == 3);
        results.get(uri).forEach(edit => {
            assert(edit.newText == newName, `'${edit.newText}' != expected '${newName}'`);
            assert(acceptableLines.has(edit.range.start.line), `${edit.range.start.line} is not in the list of acceptable lines`);
        });
    });
    test("command CompileRule", async function() {
        // should compile the active document in the current texteditor
        const cmd: string = "yara.CompileRule";
        let cmds: Array<string> = await vscode.commands.getCommands(true);
        assert(cmds.indexOf(cmd) != -1);
        let items = await vscode.commands.executeCommand(cmd);
    });
    test("command CompileAllRules with workspace", async function() {
        // should compile all .yar and .yara rules in the current workspace
        const cmd: string = "yara.CompileAllRules";
        let cmds: Array<string> = await vscode.commands.getCommands(true);
        assert(cmds.indexOf(cmd) != -1);
        let items = await vscode.commands.executeCommand(cmd);
    });
    test("command CompileAllRules without workspace", async function() {
        // should compile all dirty files in the current texteditor
        const cmd: string = "yara.CompileAllRules";
        let cmds: Array<string> = await vscode.commands.getCommands(true);
        assert(cmds.indexOf(cmd) != -1);
        let items = await vscode.commands.executeCommand(cmd);
    });
});
