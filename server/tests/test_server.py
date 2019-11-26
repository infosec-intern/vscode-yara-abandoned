import asyncio
import json
import logging
from pathlib import Path

import pytest
from yarals import custom_err as ce
from yarals import helpers
from yarals import protocol


@pytest.mark.skip(reason="not implemented")
@pytest.mark.server
def test_cmd_compile_rule():
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
    assert result[0].range.start.char == 0
    assert result[0].range.end.line == 5
    assert result[0].range.end.char == 18

@pytest.mark.asyncio
@pytest.mark.server
async def test_definitions_variables_count(test_rules, yara_server):
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
    assert result[0].range.start.char == 8
    assert result[0].range.end.line == 21
    assert result[0].range.end.char == 19

@pytest.mark.asyncio
@pytest.mark.server
async def test_definitions_variables_length(test_rules, yara_server):
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
    assert result[0].range.start.char == 8
    assert result[0].range.end.line == 40
    assert result[0].range.end.char == 22

@pytest.mark.asyncio
@pytest.mark.server
async def test_definitions_variables_location(test_rules, yara_server):
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
    assert result[0].range.start.char == 8
    assert result[0].range.end.line == 21
    assert result[0].range.end.char == 19

@pytest.mark.asyncio
@pytest.mark.server
async def test_definitions_variables_regular(test_rules, yara_server):
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
    assert result[0].range.start.char == 8
    assert result[0].range.end.line == 19
    assert result[0].range.end.char == 22

@pytest.mark.asyncio
@pytest.mark.server
async def test_no_definitions(test_rules, yara_server):
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
    document = "rule NoDiagnostics { condition: true }"
    result = await yara_server.provide_diagnostic(document)
    assert result == []

@pytest.mark.asyncio
@pytest.mark.server
async def test_dirty_files(test_rules, yara_server):
    peek_rules = str(test_rules.joinpath("peek_rules.yara").resolve())
    file_uri = helpers.create_file_uri(peek_rules)
    unsaved_changes = "rule ResolveSymbol {\n strings:\n  $a = \"test\"\n condition:\n  #a > 3\n}\n"
    dirty_files = {
        file_uri: unsaved_changes
    }
    document = yara_server._get_document(file_uri, dirty_files)
    assert document == unsaved_changes

@pytest.mark.xfail
@pytest.mark.asyncio
@pytest.mark.server
async def test_exceptions_handled():
    assert False is True

@pytest.mark.xfail
@pytest.mark.asyncio
@pytest.mark.server
async def test_exit(local_server, yara_server):
    exit_req = json.dumps({"jsonrpc":"2.0","method":"exit","params":None})
    assert exit_req is False

@pytest.mark.skip(reason="not implemented")
@pytest.mark.server
def test_highlights():
    assert False is True

@pytest.mark.asyncio
@pytest.mark.server
async def test_hover(test_rules, yara_server):
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
async def test_no_hover(test_rules, yara_server):
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
async def test_initialize(initialize_msg, local_server, yara_server):
    expected = {
        "jsonrpc": "2.0", "id": 0, "result":{
            "capabilities": {
                "completionProvider":{"resolveProvider": False, "triggerCharacters": ["."]},
                "definitionProvider": True, "hoverProvider": True,
                "referencesProvider": True, "textDocumentSync": 1,
                "executeCommandProvider": {"commands": ["yara.CompileRule", "yara.CompileAllRules"]}
            }
        }
    }
    srv_addr, srv_port = local_server
    reader, writer = await asyncio.open_connection(srv_addr, srv_port)
    message = json.dumps(initialize_msg)
    # write_data and read_request are just helpers for formatting JSON-RPC messages appropriately
    # despite using a second YaraLanguageServer, these will route through the one in local_server
    # because we pass the related reader & writer objects to these functions
    await yara_server.write_data(message, writer)
    response = await yara_server.read_request(reader)
    assert response == expected
    writer.close()
    await writer.wait_closed()

@pytest.mark.asyncio
@pytest.mark.server
async def test_no_references(test_rules, yara_server):
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
            assert location.range.start.char == 8
            assert location.range.end.line == 21
            assert location.range.end.char == 16
        elif index == 1:
            assert location.range.start.line == 28
            assert location.range.start.char == 8
            assert location.range.end.line == 28
            assert location.range.end.char == 16
        elif index == 2:
            assert location.range.start.line == 29
            assert location.range.start.char == 8
            assert location.range.end.line == 29
            assert location.range.end.char == 16

@pytest.mark.asyncio
@pytest.mark.server
async def test_references_wildcard(test_rules, yara_server):
    peek_rules = str(test_rules.joinpath("peek_rules.yara").resolve())
    file_uri = helpers.create_file_uri(peek_rules)
    params = {
        "textDocument": {"uri": file_uri},
        "position": {"line": 30, "character": 12},
        "context": {"includeDeclaration": True}
    }
    document = yara_server._get_document(file_uri, dirty_files={})
    result = await yara_server.provide_reference(params, document)
    assert len(result) == 4
    for index, location in enumerate(result):
        assert isinstance(location, protocol.Location) is True
        assert location.uri == file_uri
        if index == 0:
            assert location.range.start.line == 19
            assert location.range.start.char == 8
            assert location.range.end.line == 19
            assert location.range.end.char == 19
        elif index == 1:
            assert location.range.start.line == 20
            assert location.range.start.char == 8
            assert location.range.end.line == 20
            assert location.range.end.char == 20
        elif index == 2:
            assert location.range.start.line == 24
            assert location.range.start.char == 8
            assert location.range.end.line == 24
            assert location.range.end.char == 19
        elif index == 3:
            assert location.range.start.line == 30
            assert location.range.start.char == 8
            assert location.range.end.line == 30
            assert location.range.end.char == 13

@pytest.mark.skip(reason="not implemented")
@pytest.mark.asyncio
@pytest.mark.server
async def test_renames(test_rules, yara_server):
    peek_rules = str(test_rules.joinpath("peek_rules.yara").resolve())
    file_uri = helpers.create_file_uri(peek_rules)
    params = {
        "textDocument": {"uri": file_uri},
        "position": {"line": 29, "character": 12},
        "newName": "test_rename"
    }
    document = yara_server._get_document(file_uri, dirty_files={})
    result = await yara_server.provide_rename(params, document)
    assert len(result) == 1
    assert isinstance(result[0], protocol.WorkspaceEdit) is True

@pytest.mark.xfail
@pytest.mark.asyncio
@pytest.mark.server
async def test_shutdown(caplog, setup_server):
    shutdown_req = json.dumps({"jsonrpc":"2.0","id":1,"method":"shutdown","params":None})
    assert shutdown_req is False
