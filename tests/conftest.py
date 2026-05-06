import json
from pathlib import Path

import pytest


@pytest.fixture
def silly_tavern_jsonl(tmp_path: Path) -> Path:
    messages = [
        {"name": "User", "mes": "Start the scene in the forest."},
        {"name": "Miah", "mes": "The trees loomed tall around them.\n\nBirds sang overhead."},
        {"name": "User", "mes": "Miah looks around nervously."},
        {"name": "Miah", "mes": "Her hands trembled as she scanned the shadows.\n\nSomething moved."},
        {"name": "User", "mes": "Draw your weapon."},
        {"name": "User", "mes": "And prepare for combat."},
        {"name": "Miah", "mes": "Steel sang as the blade left its sheath.\n\nThe creature emerged."},
    ]

    file_path = tmp_path / "test_session.jsonl"
    with open(file_path, "w") as f:
        for msg in messages:
            f.write(json.dumps(msg) + "\n")

    return file_path


@pytest.fixture
def sample_turns_jsonl(tmp_path: Path) -> Path:
    messages = []
    for i in range(12):
        messages.append({"name": "User", "mes": f"Prompt {i + 1}"})
        messages.append({"name": "Miah", "mes": f"Response {i + 1}. " * 20})

    file_path = tmp_path / "long_session.jsonl"
    with open(file_path, "w") as f:
        for msg in messages:
            f.write(json.dumps(msg) + "\n")

    return file_path
