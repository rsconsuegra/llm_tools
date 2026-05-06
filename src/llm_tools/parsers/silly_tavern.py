import json
from pathlib import Path

from llm_tools.models import ChatSession, Turn
from llm_tools.parsers.base import BaseParser


class SillyTavernParser(BaseParser):
    def __init__(self, character_name: str = "Miah"):
        self.character_name = character_name

    def parse(self, source: Path | str) -> ChatSession:
        source = Path(source)
        lines = source.read_text(encoding="utf-8").strip().splitlines()

        turns: list[Turn] = []
        current_prompt_parts: list[str] = []
        turn_id = 0

        for line in lines:
            msg = json.loads(line)
            text = msg["mes"].replace("\n\n", "\n").strip()

            if msg["name"] == self.character_name:
                turn_id += 1
                turns.append(
                    Turn(
                        turn_id=turn_id,
                        prompt="\n".join(current_prompt_parts).strip(),
                        response=text,
                    )
                )
                current_prompt_parts = []
            else:
                current_prompt_parts.append(text)

        return ChatSession(
            source=str(source),
            format="sillytavern",
            turns=turns,
            character_name=self.character_name,
        )
