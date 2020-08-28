''' Tests for yarals.yarals module '''
import json
import logging

import pytest
from yarals import helpers
from yarals import protocol

try:
    # asyncio exceptions changed from 3.6 > 3.7 > 3.8
    # so try to keep this compatible regardless of Python version 3.6+
    # https://medium.com/@jflevesque/asyncio-exceptions-changes-from-python-3-6-to-3-7-to-3-8-cancellederror-timeouterror-f79945ead378
    from asyncio.exceptions import CancelledError
except ImportError:
    from concurrent.futures import CancelledError

@pytest.mark.skip(reason="not implemented")
@pytest.mark.server
def test_cmd_compile_rule():
    ''' Ensure CompileRule compiles the currently-active YARA rule file '''
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "workspace/executeCommand",
        "params": {
            "command": "yara.CompileRule",
            "arguments": []
        }
    }
    assert request is False

@pytest.mark.skip(reason="not implemented")
@pytest.mark.server
def test_cmd_compile_all_rules():
    ''' Ensure CompileAllRules compiles all YARA rule files in the given workspace '''
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "workspace/executeCommand",
        "params": {
            "command": "yara.CompileAllRules",
            "arguments": []
        }
    }
    assert request is False

@pytest.mark.skip(reason="not implemented")
@pytest.mark.server
def test_cmd_compile_all_rules_no_workspace():
    ''' Ensure CompileAllRules only compiles opened files when no workspace is specified '''
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "workspace/executeCommand",
        "params": {
            "command": "yara.CompileAllRules",
            "arguments": []
        }
    }
    assert request is False

@pytest.mark.asyncio
@pytest.mark.server
async def test_code_completion_regular(test_rules, yara_server):
    ''' Ensure code completion works with functions defined in modules schema '''
    actual = []
    code_completion = str(test_rules.joinpath("code_completion.yara").resolve())
    expected = ["network", "registry", "filesystem", "sync"]
    file_uri = helpers.create_file_uri(code_completion)
    params = {
        "textDocument": {"uri": file_uri},
        "position": {"line": 9, "character": 15}
    }
    document = yara_server._get_document(file_uri, dirty_files={})
    result = await yara_server.provide_code_completion(params, document)
    assert len(result) == 4
    for completion in result:
        assert isinstance(completion, protocol.CompletionItem) is True
        actual.append(completion.label)
    assert actual == expected

@pytest.mark.asyncio
@pytest.mark.server
async def test_code_completion_overflow(test_rules, yara_server):
    ''' Ensure code completion doesn't return items or error out when a position doesn't exist in the file '''
    code_completion = str(test_rules.joinpath("code_completion.yara").resolve())
    file_uri = helpers.create_file_uri(code_completion)
    params = {
        "textDocument": {"uri": file_uri},
        "position": {"line": 9, "character": 25}
    }
    document = yara_server._get_document(file_uri, dirty_files={})
    result = await yara_server.provide_code_completion(params, document)
    assert result == []

@pytest.mark.asyncio
@pytest.mark.server
async def test_code_completion_unexpected(test_rules, yara_server):
    ''' Ensure code completion doesn't return items or error out when a symbol does not have any items to be completed '''
    code_completion = str(test_rules.joinpath("code_completion.yara").resolve())
    file_uri = helpers.create_file_uri(code_completion)
    params = {
        "textDocument": {"uri": file_uri},
        "position": {"line": 8, "character": 25}
    }
    document = yara_server._get_document(file_uri, dirty_files={})
    result = await yara_server.provide_code_completion(params, document)
    assert result == []

@pytest.mark.asyncio
@pytest.mark.server
async def test_definitions_rules(test_rules, yara_server):
    ''' Ensure definition is provided for a rule name '''
    peek_rules = str(test_rules.joinpath("peek_rules.yara").resolve())
    file_uri = helpers.create_file_uri(peek_rules)
    params = {
        "textDocument": {"uri": file_uri},
        "position": {"line": 42, "character": 12}
    }
    document = yara_server._get_document(file_uri, dirty_files={})
    result = await yara_server.provide_definition(params, document)
    assert len(result) == 1
    assert isinstance(result[0], protocol.Location) is True
    assert result[0].uri == file_uri
    assert result[0].range.start.line == 5
    assert result[0].range.start.char == 5
    assert result[0].range.end.line == 5
    assert result[0].range.end.char == 18

@pytest.mark.asyncio
@pytest.mark.server
async def test_definitions_private_rules(test_rules, yara_server):
    ''' Ensure definition is provided for a private rule name '''
    private_goto_rules = str(test_rules.joinpath("private_rule_goto.yara").resolve())
    file_uri = helpers.create_file_uri(private_goto_rules)
    params = {
        "textDocument": {"uri": file_uri},
        "position": {"line": 9, "character": 14}
    }
    document = yara_server._get_document(file_uri, dirty_files={})
    result = await yara_server.provide_definition(params, document)
    assert len(result) == 1
    assert isinstance(result[0], protocol.Location) is True
    assert result[0].uri == file_uri
    assert result[0].range.start.line == 0
    assert result[0].range.start.char == 13
    assert result[0].range.end.line == 0
    assert result[0].range.end.char == 28

@pytest.mark.asyncio
@pytest.mark.server
async def test_definitions_variables_count(test_rules, yara_server):
    ''' Ensure definition is provided for a variable with count modifier (#) '''
    peek_rules = str(test_rules.joinpath("peek_rules.yara").resolve())
    file_uri = helpers.create_file_uri(peek_rules)
    params = {
        "textDocument": {"uri": file_uri},
        "position": {"line": 28, "character": 12}
    }
    document = yara_server._get_document(file_uri, dirty_files={})
    result = await yara_server.provide_definition(params, document)
    assert len(result) == 1
    assert isinstance(result[0], protocol.Location) is True
    assert result[0].uri == file_uri
    assert result[0].range.start.line == 21
    assert result[0].range.start.char == 9
    assert result[0].range.end.line == 21
    assert result[0].range.end.char == 19

@pytest.mark.asyncio
@pytest.mark.server
async def test_definitions_variables_length(test_rules, yara_server):
    ''' Ensure definition is provided for a variable with length modifier (!) '''
    peek_rules = str(test_rules.joinpath("peek_rules.yara").resolve())
    file_uri = helpers.create_file_uri(peek_rules)
    params = {
        "textDocument": {"uri": file_uri},
        "position": {"line": 42, "character": 32}
    }
    document = yara_server._get_document(file_uri, dirty_files={})
    result = await yara_server.provide_definition(params, document)
    assert len(result) == 1
    assert isinstance(result[0], protocol.Location) is True
    assert result[0].uri == file_uri
    assert result[0].range.start.line == 40
    assert result[0].range.start.char == 9
    assert result[0].range.end.line == 40
    assert result[0].range.end.char == 22

@pytest.mark.asyncio
@pytest.mark.server
async def test_definitions_variables_location(test_rules, yara_server):
    ''' Ensure definition is provided for a variable with location modifier (@) '''
    peek_rules = str(test_rules.joinpath("peek_rules.yara").resolve())
    file_uri = helpers.create_file_uri(peek_rules)
    params = {
        "textDocument": {"uri": file_uri},
        "position": {"line": 29, "character": 12}
    }
    document = yara_server._get_document(file_uri, dirty_files={})
    result = await yara_server.provide_definition(params, document)
    assert len(result) == 1
    assert isinstance(result[0], protocol.Location) is True
    assert result[0].uri == file_uri
    assert result[0].range.start.line == 21
    assert result[0].range.start.char == 9
    assert result[0].range.end.line == 21
    assert result[0].range.end.char == 19

@pytest.mark.asyncio
@pytest.mark.server
async def test_definitions_variables_regular(test_rules, yara_server):
    ''' Ensure definition is provided for a normal variable '''
    peek_rules = str(test_rules.joinpath("peek_rules.yara").resolve())
    file_uri = helpers.create_file_uri(peek_rules)
    params = {
        "textDocument": {"uri": file_uri},
        "position": {"line": 24, "character": 12}
    }
    document = yara_server._get_document(file_uri, dirty_files={})
    result = await yara_server.provide_definition(params, document)
    assert len(result) == 1
    assert isinstance(result[0], protocol.Location) is True
    assert result[0].uri == file_uri
    assert result[0].range.start.line == 19
    assert result[0].range.start.char == 9
    assert result[0].range.end.line == 19
    assert result[0].range.end.char == 22

@pytest.mark.asyncio
@pytest.mark.server
async def test_no_definitions(test_rules, yara_server):
    ''' Ensure no definition is provided for symbols that are not variables or rules '''
    peek_rules = str(test_rules.joinpath("peek_rules.yara").resolve())
    file_uri = helpers.create_file_uri(peek_rules)
    params = {
        "textDocument": {"uri": file_uri},
        "position": {"line": 27, "character": 12},
        "context": {"includeDeclaration": True}
    }
    document = yara_server._get_document(file_uri, dirty_files={})
    result = await yara_server.provide_definition(params, document)
    assert result == []

@pytest.mark.asyncio
@pytest.mark.server
async def test_diagnostics(yara_server):
    ''' Ensure a diagnostic error message is provided when appropriate '''
    document = "rule OneDiagnostic { condition: $true }"
    result = await yara_server.provide_diagnostic(document)
    assert len(result) == 1
    diagnostic = result[0]
    assert isinstance(diagnostic, protocol.Diagnostic) is True
    assert diagnostic.severity == 1
    assert diagnostic.message == "undefined string \"$true\""
    assert diagnostic.range.start.line == 0
    assert diagnostic.range.end.line == 0

@pytest.mark.asyncio
@pytest.mark.server
async def test_no_diagnostics(yara_server):
    ''' Ensure no diagnostics are provided when rules are successfully compiled '''
    document = "rule NoDiagnostics { condition: true }"
    result = await yara_server.provide_diagnostic(document)
    assert result == []

@pytest.mark.asyncio
@pytest.mark.server
async def test_dirty_files(test_rules, yara_server):
    ''' Ensure server prefers versions of dirty files over those backed by file path '''
    peek_rules = str(test_rules.joinpath("peek_rules.yara").resolve())
    file_uri = helpers.create_file_uri(peek_rules)
    unsaved_changes = "rule ResolveSymbol {\n strings:\n  $a = \"test\"\n condition:\n  #a > 3\n}\n"
    dirty_files = {
        file_uri: unsaved_changes
    }
    document = yara_server._get_document(file_uri, dirty_files)
    assert document == unsaved_changes

@pytest.mark.asyncio
@pytest.mark.server
async def test_exceptions_handled(initialize_msg, initialized_msg, open_streams, test_rules, yara_server):
    ''' Ensure server notifies user when errors are encountered '''
    expected = {
        "jsonrpc": "2.0", "method": "window/showMessage",
        "params": {"type": 1, "message": "Could not find symbol for definition request"}
    }
    peek_rules = str(test_rules.joinpath("peek_rules.yara").resolve())
    file_uri = helpers.create_file_uri(peek_rules)
    error_request = json.dumps({
        "jsonrpc": "2.0", "id": 1,    # the initialize message takes id 0
        "method": "textDocument/definition",
        "params": {
            "textDocument": {"uri": file_uri},
            "position": {}
        }
    })
    reader, writer = open_streams
    await yara_server.write_data(initialize_msg, writer)
    await yara_server.read_request(reader)
    await yara_server.write_data(initialized_msg, writer)
    await yara_server.read_request(reader)
    await yara_server.write_data(error_request, writer)
    response = await yara_server.read_request(reader)
    assert response == expected
    writer.close()
    await writer.wait_closed()

@pytest.mark.asyncio
@pytest.mark.server
async def test_exit(caplog, initialize_msg, initialized_msg, open_streams, shutdown_msg, yara_server):
    ''' Ensure the server shuts down when given the proper shutdown/exit sequence '''
    exit_msg = json.dumps({"jsonrpc":"2.0","method":"exit","params":None})
    reader, writer = open_streams
    with pytest.raises(CancelledError):
        with caplog.at_level(logging.DEBUG, "yara"):
            await yara_server.write_data(initialize_msg, writer)
            await yara_server.read_request(reader)
            await yara_server.write_data(initialized_msg, writer)
            await yara_server.read_request(reader)
            await yara_server.write_data(shutdown_msg, writer)
            await yara_server.read_request(reader)
            await yara_server.write_data(exit_msg, writer)
            await yara_server.read_request(reader)
            assert ("yara", logging.INFO, "Disconnected client") in caplog.record_tuples
            assert ("yara", logging.ERROR, "Server exiting process per client request") in caplog.record_tuples
    writer.close()
    await writer.wait_closed()

@pytest.mark.skip(reason="not implemented")
@pytest.mark.server
def test_highlights():
    ''' TBD '''
    assert False is True

@pytest.mark.asyncio
@pytest.mark.server
async def test_hover(test_rules, yara_server):
    ''' Ensure a variable's value is provided on hover '''
    peek_rules = str(test_rules.joinpath("peek_rules.yara").resolve())
    file_uri = helpers.create_file_uri(peek_rules)
    params = {
        "textDocument": {"uri": file_uri},
        "position": {"line": 29, "character": 12}
    }
    document = yara_server._get_document(file_uri, dirty_files={})
    result = await yara_server.provide_hover(params, document)
    assert isinstance(result, protocol.Hover) is True
    assert result.contents.kind == protocol.MarkupKind.Plaintext
    assert result.contents.value == "\"double string\" wide nocase fullword"

@pytest.mark.asyncio
@pytest.mark.server
async def test_hover_dirty_file(initialize_msg, initialized_msg, open_streams, test_rules, yara_server):
    ''' Ensure a variable's value is provided on hover for a dirty file '''
    peek_rules = str(test_rules.joinpath("peek_rules.yara").resolve())
    file_uri = helpers.create_file_uri(peek_rules)
    unsaved_changes = "rule ResolveSymbol {\n strings:\n  $a = \"test\"\n condition:\n  #a > 3\n}\n"
    did_change_msg = json.dumps({
        "jsonrpc": "2.0", "method": "textDocument/didChange",
        "params": {
            "textDocument": {"uri": file_uri},
            "contentChanges": [{"text": unsaved_changes}]
        }
    })
    hover_msg = json.dumps({
        "jsonrpc": "2.0", "method": "textDocument/hover", "id": 2,
        "params": {
            "textDocument": {"uri": file_uri},
            "position": {"line": 4, "character": 3}
        }
    })
    reader, writer = open_streams
    await yara_server.write_data(initialize_msg, writer)
    await yara_server.read_request(reader)
    await yara_server.write_data(initialized_msg, writer)
    await yara_server.read_request(reader)
    await yara_server.write_data(did_change_msg, writer)
    await yara_server.write_data(hover_msg, writer)
    response = await yara_server.read_request(reader)
    # TODO: build JSON decoder to convert JSON objects to protocol objects
    assert response["result"]["contents"]["kind"] == "plaintext"
    assert response["result"]["contents"]["value"] == "\"test\""
    writer.close()
    await writer.wait_closed()

@pytest.mark.asyncio
@pytest.mark.server
async def test_no_hover(test_rules, yara_server):
    ''' Ensure non-variables do not return hovers '''
    peek_rules = str(test_rules.joinpath("peek_rules.yara").resolve())
    file_uri = helpers.create_file_uri(peek_rules)
    params = {
        "textDocument": {"uri": file_uri},
        "position": {"line": 25, "character": 12}
    }
    document = yara_server._get_document(file_uri, dirty_files={})
    result = await yara_server.provide_hover(params, document)
    assert result is None

@pytest.mark.asyncio
@pytest.mark.server
async def test_initialize(initialize_msg, initialized_msg, open_streams, yara_server):
    ''' Ensure server responds with appropriate initialization handshake '''
    expected_initialize = {
        "jsonrpc": "2.0", "id": 0, "result":{
            "capabilities": {
                "completionProvider":{"resolveProvider": False, "triggerCharacters": ["."]},
                "definitionProvider": True, "hoverProvider": True, "renameProvider": True,
                "referencesProvider": True, "textDocumentSync": 1,
                "executeCommandProvider": {"commands": ["yara.CompileRule", "yara.CompileAllRules"]}
            }
        }
    }
    expected_initialized = {
        "jsonrpc": "2.0", "method": "window/showMessageRequest",
        "params": {"type": 3, "message": "Successfully connected"}
    }
    reader, writer = open_streams
    # write_data and read_request are just helpers for formatting JSON-RPC messages appropriately
    # despite using a second YaraLanguageServer, these will route through the one in local_server
    # because we pass the related reader & writer objects to these functions
    await yara_server.write_data(initialize_msg, writer)
    response = await yara_server.read_request(reader)
    assert response == expected_initialize
    await yara_server.write_data(initialized_msg, writer)
    response = await yara_server.read_request(reader)
    assert response == expected_initialized
    writer.close()
    await writer.wait_closed()

@pytest.mark.asyncio
@pytest.mark.server
async def test_no_references(test_rules, yara_server):
    ''' Ensure server does not return references if none are found '''
    alienspy = str(test_rules.joinpath("apt_alienspy_rat.yar").resolve())
    file_uri = helpers.create_file_uri(alienspy)
    params = {
        "textDocument": {"uri": file_uri},
        "position": {"line": 47, "character": 99},
    }
    document = yara_server._get_document(file_uri, dirty_files={})
    result = await yara_server.provide_reference(params, document)
    assert result == []

@pytest.mark.asyncio
@pytest.mark.server
async def test_references_rules(test_rules, yara_server):
    ''' Ensure references to rules are returned at the start of the rule name '''
    peek_rules = str(test_rules.joinpath("peek_rules.yara").resolve())
    file_uri = helpers.create_file_uri(peek_rules)
    params = {
        "textDocument": {"uri": file_uri},
        "position": {"line": 42, "character": 12},
        "context": {"includeDeclaration": True}
    }
    document = yara_server._get_document(file_uri, dirty_files={})
    result = await yara_server.provide_reference(params, document)
    assert len(result) == 2
    for index, location in enumerate(result):
        assert isinstance(location, protocol.Location) is True
        assert location.uri == file_uri
        if index == 0:
            assert location.range.start.line == 5
            assert location.range.start.char == 5
            assert location.range.end.line == 5
            assert location.range.end.char == 18
        elif index == 1:
            assert location.range.start.line == 42
            assert location.range.start.char == 8
            assert location.range.end.line == 42
            assert location.range.end.char == 21

@pytest.mark.asyncio
@pytest.mark.server
async def test_references_variable(test_rules, yara_server):
    ''' Ensure references to variables are returned at the start of the variable name '''
    peek_rules = str(test_rules.joinpath("peek_rules.yara").resolve())
    file_uri = helpers.create_file_uri(peek_rules)
    params = {
        "textDocument": {"uri": file_uri},
        "position": {"line": 28, "character": 12},
        "context": {"includeDeclaration": True}
    }
    document = yara_server._get_document(file_uri, dirty_files={})
    result = await yara_server.provide_reference(params, document)
    assert len(result) == 3
    for index, location in enumerate(result):
        assert isinstance(location, protocol.Location) is True
        assert location.uri == file_uri
        if index == 0:
            assert location.range.start.line == 21
            assert location.range.start.char == 9
            assert location.range.end.line == 21
            assert location.range.end.char == 16
        elif index == 1:
            assert location.range.start.line == 28
            assert location.range.start.char == 9
            assert location.range.end.line == 28
            assert location.range.end.char == 16
        elif index == 2:
            assert location.range.start.line == 29
            assert location.range.start.char == 9
            assert location.range.end.line == 29
            assert location.range.end.char == 16

@pytest.mark.asyncio
@pytest.mark.server
async def test_references_wildcard(test_rules, yara_server):
    ''' Ensure wildcard variables return references to all possible variables within rule they are found '''
    peek_rules = str(test_rules.joinpath("peek_rules.yara").resolve())
    file_uri = helpers.create_file_uri(peek_rules)
    params = {
        "textDocument": {"uri": file_uri},
        "position": {"line": 30, "character": 11},
        "context": {"includeDeclaration": True}
    }
    document = yara_server._get_document(file_uri, dirty_files={})
    result = await yara_server.provide_reference(params, document)
    assert len(result) == 2
    for index, location in enumerate(result):
        assert isinstance(location, protocol.Location) is True
        assert location.uri == file_uri
        if index == 0:
            assert location.range.start.line == 19
            assert location.range.start.char == 9
            assert location.range.end.line == 19
            assert location.range.end.char == 19
        elif index == 1:
            assert location.range.start.line == 20
            assert location.range.start.char == 9
            assert location.range.end.line == 20
            assert location.range.end.char == 20

@pytest.mark.asyncio
@pytest.mark.server
async def test_renames(test_rules, yara_server):
    ''' Ensure variables can be renamed '''
    peek_rules = str(test_rules.joinpath("peek_rules.yara").resolve())
    file_uri = helpers.create_file_uri(peek_rules)
    # @dstring[1]: Line 30, Col 12
    new_text = "test_rename"
    params = {
        "textDocument": {"uri": file_uri},
        "position": {"line": 29, "character": 12},
        "newName": new_text
    }
    document = yara_server._get_document(file_uri, dirty_files={})
    result = await yara_server.provide_rename(params, document, file_uri)
    assert isinstance(result, protocol.WorkspaceEdit) is True
    assert len(result.changes) == 3
    acceptable_lines = [21, 28, 29]
    for edit in result.changes:
        assert isinstance(edit, protocol.TextEdit) is True
        assert edit.newText == new_text
        assert edit.range.start.line in acceptable_lines

@pytest.mark.asyncio
@pytest.mark.server
async def test_shutdown(caplog, initialize_msg, initialized_msg, open_streams, shutdown_msg, yara_server):
    ''' Ensure server logs appropriate response to shutdown '''
    reader, writer = open_streams
    with caplog.at_level(logging.DEBUG, "yara"):
        await yara_server.write_data(initialize_msg, writer)
        await yara_server.read_request(reader)
        await yara_server.write_data(initialized_msg, writer)
        await yara_server.read_request(reader)
        await yara_server.write_data(shutdown_msg, writer)
        await yara_server.read_request(reader)
        assert ("yara", logging.INFO, "Client requested shutdown") in caplog.record_tuples
    writer.close()
    await writer.wait_closed()
