import json
from typing import List

from interfaces.character import CharacterInScene
from interfaces.shot import ShotBriefDescription
from tools.groq_llm import GroqLLM
from tools.json_utils import parse_json_object


def _fallback_storyboard(script: str) -> str:
    compact = " ".join((script or "A new story begins.").split())
    return json.dumps(
        {
            "shots": [
                {
                    "idx": 0,
                    "visual_desc": f"Wide establishing view. {compact[:190]}",
                    "motion_desc": "Slow cinematic push-in that introduces the location and mood.",
                    "audio_desc": "Soft ambient sound with a subtle opening music cue.",
                },
                {
                    "idx": 1,
                    "visual_desc": f"Medium character-focused composition showing the key decision. {compact[190:390]}",
                    "motion_desc": "Gentle side movement with a closer framing on the emotional action.",
                    "audio_desc": "Natural room tone and a restrained emotional music layer.",
                },
                {
                    "idx": 2,
                    "visual_desc": "Clean closing image that resolves the scene and leaves one memorable visual symbol.",
                    "motion_desc": "Slow pull-back, holding on the final image before fading out.",
                    "audio_desc": "A short resolving musical note and fading ambience.",
                },
            ]
        }
    )


class StoryboardArtist:
    def __init__(self):
        self.llm = GroqLLM()

    async def design_storyboard(
        self,
        script: str,
        characters: List[CharacterInScene],
        user_requirement: str,
    ) -> List[ShotBriefDescription]:
        cast = "\n".join(
            f"- {character.name}: {character.static_features}; {character.dynamic_features}"
            for character in characters
            if character.is_visible
        )
        system_prompt = (
            "You are a storyboard artist. Convert one short scene into exactly three clear shots for a motion-comic video. "
            "Return only valid JSON."
        )
        prompt = f"""Storyboard this scene:

{script}

Visible characters:
{cast or 'No named character'}

Style: {user_requirement or 'clean cinematic'}

Return:
{{"shots":[{{"idx":0,"visual_desc":"...","motion_desc":"...","audio_desc":"..."}}]}}
Use exactly three shots: establishing, emotional action, closing image."""
        fallback = _fallback_storyboard(script)
        raw = await self.llm.complete(prompt, system_prompt=system_prompt, timeout=90, fallback=fallback)
        try:
            data = parse_json_object(raw)
            shots = [ShotBriefDescription(**item) for item in data.get("shots", [])[:3]]
            if shots:
                return shots
        except Exception:
            pass
        return [ShotBriefDescription(**item) for item in parse_json_object(fallback)["shots"]]
