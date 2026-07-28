import json
from typing import List

from tools.groq_llm import GroqLLM
from tools.json_utils import parse_json_object


def _fallback_story(idea: str, requirement: str) -> str:
    premise = idea.strip() or "A creator discovers that one small decision can change an entire day."
    extra = requirement.strip()
    return (
        f"Title: One More Chance\n\n"
        f"The story begins with {premise.rstrip('.')}. The protagonist wants to move forward but faces a clear "
        "emotional obstacle. A small clue changes the direction of the story, leading to a visual confrontation "
        "and a hopeful final choice. The drama is designed as a concise, character-led short with a strong opening, "
        f"a turning point, and a memorable closing image. {extra}"
    ).strip()


def _fallback_scenes(story: str) -> str:
    compact = " ".join(story.split())[:420]
    return json.dumps(
        {
            "scenes": [
                {
                    "scene_number": 1,
                    "title": "The Spark",
                    "script": (
                        "INT. CREATIVE STUDIO - MORNING\n"
                        f"A quiet room wakes with soft daylight. {compact} "
                        "The protagonist notices a detail that no one else sees and decides to act."
                    ),
                },
                {
                    "scene_number": 2,
                    "title": "The Choice",
                    "script": (
                        "EXT. CITY ROOFTOP - GOLDEN HOUR\n"
                        "The protagonist reaches the final decision point. The noise of the city fades. "
                        "A small, honest action resolves the conflict and leaves a hopeful final image."
                    ),
                },
            ]
        }
    )


class Screenwriter:
    def __init__(self):
        self.llm = GroqLLM()

    async def develop_story(self, idea: str, user_requirement: str) -> str:
        system_prompt = (
            "You are a professional short-form screenwriter. Expand ideas into visually clear, emotionally coherent "
            "micro-drama outlines for videos under two minutes. Keep the result practical to storyboard."
        )
        prompt = f"""Develop a short visual story from this idea:

Idea: {idea}
Creator requirements: {user_requirement or 'None'}

Include the setting, protagonist, goal, obstacle, turning point, visual climax, and resolution. Write flowing prose."""
        return await self.llm.complete(
            prompt,
            system_prompt=system_prompt,
            timeout=90,
            fallback=_fallback_story(idea, user_requirement),
        )

    async def write_script_based_on_story(self, story: str, user_requirement: str) -> List[str]:
        system_prompt = (
            "You are a screenwriter. Split a short outline into exactly two concise, filmable scenes. "
            "Return only valid JSON with no markdown."
        )
        prompt = f"""Create two scene scripts from this outline:

{story}

Requirements: {user_requirement or 'None'}

Return:
{{"scenes":[{{"scene_number":1,"title":"...","script":"..."}}]}}
Each scene must include setting, action, optional dialogue, and a clear visual ending."""
        raw = await self.llm.complete(
            prompt,
            system_prompt=system_prompt,
            timeout=90,
            fallback=_fallback_scenes(story),
        )
        try:
            data = parse_json_object(raw)
            scenes = [str(scene.get("script", "")).strip() for scene in data.get("scenes", [])]
            scenes = [scene for scene in scenes if scene]
            return scenes[:3] or [story]
        except Exception:
            data = parse_json_object(_fallback_scenes(story))
            return [scene["script"] for scene in data["scenes"]]
