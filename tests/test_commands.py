from animyst.commands import CommandDispatcher, parse_command


def test_parse_command_splits_name_and_args():
    parsed = parse_command("awaken scout")

    assert parsed.name == "awaken"
    assert parsed.args == ["scout"]


def test_dispatcher_handles_manifest_without_args():
    action = CommandDispatcher().dispatch("manifest")

    assert action.kind == "manifest_agent"


def test_dispatcher_treats_manifest_with_name_as_run():
    action = CommandDispatcher().dispatch("manifest scout")

    assert action.kind == "run_agent"
    assert action.args == ["scout"]


def test_dispatcher_routes_unknown_commands():
    action = CommandDispatcher().dispatch("summon portal")

    assert action.kind == "unknown"
    assert action.payload["command"] == "summon portal"

