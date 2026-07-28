import json
import re
from typing import List

from interfaces.character import CharacterInScene
from tools.groq_llm import GroqLLM
from tools.json_utils import parse_json_object


def _fallback_characters(script: str) -> str:
    candidates = re.findall(r"\b[A-Z][A-Za-z]{2,}\b", script or "")
    ignored = {"INT", "EXT", "DAY", "NIGHT", "MORNING", "EVENING", "DESIGN", "STUDIO", "ROOM", "CITY", "HOME", "OFFICE", "THE", "The", "A", "An"}
    name = next((candidate for candidate in candidates if candidate not in ignored), "Maya")
    return json.dumps(
        {
            "characters": [
                {
                    "idx": 0,
                    "name": name,
                    "static_features": "Young adult with expressive eyes, a natural face, and a confident creative presence",
                    "dynamic_features": "Clean modern outfit with a green accent and practical everyday accessories",
                    "is_visible": True,
                }
            ]
        }
    )


class CharacterExtractor:
    def __init__(self):
        self.llm = GroqLLM()

    async def extract_characters(self, script: str) -> List[CharacterInScene]:
        system_prompt = (
            "You are a casting and continuity assistant. Extract only visible characters and describe them consistently. "
            "Return only valid JSON."
        )
        prompt = f"""Extract visible characters from this script:

{script}

Return:
{{"characters":[{{"idx":0,"name":"Name","static_features":"physical description","dynamic_features":"clothes and accessories","is_visible":true}}]}}
Limit the result to three important characters."""
        fallback = _fallback_characters(script)
        raw = await self.llm.complete(prompt, system_prompt=system_prompt, timeout=90, fallback=fallback)
        try:
            data = parse_json_object(raw)
            characters = [CharacterInScene(**item) for item in data.get("characters", [])[:3]]
            return characters or [CharacterInScene(**parse_json_object(fallback)["characters"][0])]
        except Exception:
            return [CharacterInScene(**parse_json_object(fallback)["characters"][0])]
