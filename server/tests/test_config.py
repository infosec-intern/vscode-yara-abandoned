import asyncio

import pytest
from yarals import helpers


@pytest.mark.xfail
@pytest.mark.config
def test_compile_on_save_false(test_rules):
    change_config_request = {
        "jsonrpc":"2.0",
        "method": "workspace/didChangeConfiguration",
        "params": {
            "settings": {
                "yara": {"compile_on_save": False}
            }
        }
    }
    save_file = str(test_rules.joinpath("simple_mistake.yar").resolve())
    save_request = {
        "jsonrpc": "2.0",
        "method":"textDocument/didSave",
        "params": {
            "textDocument": {
                "uri": helpers.create_file_uri(save_file),
                "version": 2
            }
        }
    }
    assert "fake news" is True

@pytest.mark.xfail
@pytest.mark.config
def test_compile_on_save_true(test_rules):
    change_config_request = {
        "jsonrpc":"2.0",
        "method": "workspace/didChangeConfiguration",
        "params": {
            "settings": {
                "yara": {"compile_on_save": True}
            }
        }
    }
    save_file = str(test_rules.joinpath("simple_mistake.yar").resolve())
    save_request = {
        "jsonrpc": "2.0",
        "method":"textDocument/didSave",
        "params": {
            "textDocument": {
                "uri": helpers.create_file_uri(save_file),
                "version": 2
            }
        }
    }
    assert "fake news" is True
