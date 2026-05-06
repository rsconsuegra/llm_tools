from llm_tools.parsers.silly_tavern import SillyTavernParser


def test_parse_basic_session(silly_tavern_jsonl):
    parser = SillyTavernParser(character_name="Miah")
    session = parser.parse(silly_tavern_jsonl)

    assert session.format == "sillytavern"
    assert session.character_name == "Miah"
    assert len(session.turns) == 3


def test_turn_pairing(silly_tavern_jsonl):
    parser = SillyTavernParser(character_name="Miah")
    session = parser.parse(silly_tavern_jsonl)

    first = session.turns[0]
    assert first.turn_id == 1
    assert "Start the scene" in first.prompt
    assert "trees loomed" in first.response


def test_multi_prompt_grouping(silly_tavern_jsonl):
    parser = SillyTavernParser(character_name="Miah")
    session = parser.parse(silly_tavern_jsonl)

    third = session.turns[2]
    assert "Draw your weapon" in third.prompt
    assert "prepare for combat" in third.prompt
    assert "Steel sang" in third.response


def test_long_session_chunking(sample_turns_jsonl):
    parser = SillyTavernParser(character_name="Miah")
    session = parser.parse(sample_turns_jsonl)

    assert len(session.turns) == 12

    from llm_tools.pipelines.summarize import _group_turns

    groups = _group_turns(session, turns_per_chunk=4)
    assert len(groups) == 3
    assert all(len(g) == 4 for g in groups)


def test_custom_character_name(tmp_path):
    import json

    messages = [
        {"name": "User", "mes": "Hello"},
        {"name": "Lunessa", "mes": "Hi there"},
    ]
    file_path = tmp_path / "custom_char.jsonl"
    with open(file_path, "w") as f:
        for msg in messages:
            f.write(json.dumps(msg) + "\n")

    parser = SillyTavernParser(character_name="Lunessa")
    session = parser.parse(file_path)

    assert len(session.turns) == 1
    assert session.character_name == "Lunessa"
