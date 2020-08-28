''' Tests for yarals.protocol module '''
import json

import pytest
from yarals import protocol


@pytest.mark.protocol
def test_diagnostic():
    ''' Ensure Diagnostic is properly encoded to JSON dictionaries '''
    pos_dict = {"line": 10, "character": 15}
    pos = protocol.Position(line=pos_dict["line"], char=pos_dict["character"])
    rg_dict = {"start": pos_dict, "end": pos_dict}
    rg_obj = protocol.Range(start=pos, end=pos)
    diag_dict = {
        "message": "Test Diagnostic",
        "range": rg_dict,
        "relatedInformation": [],
        "severity": 1
    }
    diag = protocol.Diagnostic(
        locrange=rg_obj,
        message=diag_dict["message"],
        severity=diag_dict["severity"]
    )
    assert json.dumps(diag, cls=protocol.JSONEncoder) == json.dumps(diag_dict)

@pytest.mark.protocol
def test_completionitem():
    ''' Ensure CompletionItem is properly encoded to JSON dictionaries '''
    comp_dict = {"label": "test", "kind": protocol.CompletionItemKind.CLASS}
    comp = protocol.CompletionItem(label=comp_dict["label"], kind=comp_dict["kind"])
    assert json.dumps(comp, cls=protocol.JSONEncoder) == json.dumps(comp_dict)

@pytest.mark.protocol
def test_location():
    ''' Ensure Location is properly encoded to JSON dictionaries '''
    pos_dict = {"line": 10, "character": 15}
    pos = protocol.Position(line=pos_dict["line"], char=pos_dict["character"])
    rg_dict = {"start": pos_dict, "end": pos_dict}
    rg_obj = protocol.Range(start=pos, end=pos)
    loc_dict = {"range": rg_dict, "uri": "fake:///one/two/three/four.path"}
    loc = protocol.Location(
        locrange=rg_obj,
        uri=loc_dict["uri"]
    )
    assert json.dumps(loc, cls=protocol.JSONEncoder) == json.dumps(loc_dict)

@pytest.mark.protocol
def test_position():
    ''' Ensure Position is properly encoded to JSON dictionaries '''
    pos_dict = {"line": 10, "character": 15}
    pos = protocol.Position(line=pos_dict["line"], char=pos_dict["character"])
    assert json.dumps(pos, cls=protocol.JSONEncoder) == json.dumps(pos_dict)

@pytest.mark.protocol
def test_range():
    ''' Ensure Range is properly encoded to JSON dictionaries '''
    pos_dict = {"line": 10, "character": 15}
    pos = protocol.Position(line=pos_dict["line"], char=pos_dict["character"])
    rg_dict = {"start": pos_dict, "end": pos_dict}
    rg_obj = protocol.Range(
        start=pos,
        end=pos
    )
    assert json.dumps(rg_obj, cls=protocol.JSONEncoder) == json.dumps(rg_dict)
