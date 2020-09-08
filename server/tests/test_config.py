''' Tests for yarals configuration reactions '''
import json
import logging

import pytest
from yarals import helpers, protocol


@pytest.mark.asyncio
@pytest.mark.config
async def test_compile_on_save_false(caplog, init_server, open_streams, test_rules, yara_server):
    ''' Ensure no diagnostics returned on save when 'compile_on_save' set to false '''
    new_config = {"compile_on_save": False}
    peek_rules = str(test_rules.joinpath("peek_rules.yara").resolve())
    file_uri = helpers.create_file_uri(peek_rules)
    change_config_msg = json.dumps({
        "jsonrpc":"2.0", "method": "workspace/didChangeConfiguration",
        "params": {"settings": {"yara": new_config}}
    })
    save_file_msg = json.dumps({
        "jsonrpc":"2.0", "method": "textDocument/didSave",
        "params": {"textDocument": {"uri": file_uri}}
    })
    reader, writer = open_streams
    with caplog.at_level(logging.DEBUG, "yara"):
        await init_server(reader, writer, yara_server)
        await yara_server.write_data(change_config_msg, writer)
        await yara_server.write_data(save_file_msg, writer)
        response = await yara_server.read_request(reader)
        diagnostics = response["params"]["diagnostics"]
        assert len(diagnostics) == 0
        assert ("yara", logging.DEBUG, "Changed workspace config to {}".format(json.dumps(new_config))) in caplog.record_tuples
    writer.close()
    await writer.wait_closed()

@pytest.mark.asyncio
@pytest.mark.config
async def test_compile_on_save_true(caplog, init_server, open_streams, test_rules, yara_server):
    ''' Ensure diagnostics are returned on save when 'compile_on_save' set to true '''
    expected_msg = "syntax error, unexpected <true>, expecting text string"
    expected_sev = protocol.DiagnosticSeverity.ERROR
    new_config = {"compile_on_save": True}
    peek_rules = str(test_rules.joinpath("peek_rules.yara").resolve())
    file_uri = helpers.create_file_uri(peek_rules)
    change_config_msg = json.dumps({
        "jsonrpc":"2.0", "method": "workspace/didChangeConfiguration",
        "params": {"settings": {"yara": new_config}}
    })
    save_file_msg = json.dumps({
        "jsonrpc":"2.0", "method": "textDocument/didSave",
        "params": {"textDocument": {"uri": file_uri}}
    })
    reader, writer = open_streams
    with caplog.at_level(logging.DEBUG, "yara"):
        await init_server(reader, writer, yara_server)
        await yara_server.write_data(change_config_msg, writer)
        await yara_server.write_data(save_file_msg, writer)
        response = await yara_server.read_request(reader)
        diagnostics = response["params"]["diagnostics"]
        assert len(diagnostics) == 1
        assert diagnostics[0]["message"] == expected_msg
        assert diagnostics[0]["severity"] == expected_sev
        assert ("yara", logging.DEBUG, "Changed workspace config to {}".format(json.dumps(new_config))) in caplog.record_tuples
    writer.close()
    await writer.wait_closed()
