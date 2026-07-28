from pathlib import Path
from typing import Awaitable, Callable, Optional

from agents.character_extractor import CharacterExtractor
from agents.screenwriter import Screenwriter
from pipelines.script2video import Script2VideoPipeline
from utils.video import concatenate_videos


ProgressCallback = Callable[[str, str, int], Awaitable[None]]


class Idea2VideoPipeline:
    def __init__(self, outputs_root: Optional[Path] = None):
        self.outputs_root = Path(outputs_root or "outputs")
        self.screenwriter = Screenwriter()
        self.character_extractor = CharacterExtractor()
        self.script2video = Script2VideoPipeline(asset_dir=self.outputs_root / "generated_assets")

    async def run(
        self,
        idea: str,
        user_requirement: str,
        style: str,
        job_id: str,
        progress_callback: ProgressCallback,
        creator_name: str = "Ayett",
    ) -> str:
        output_dir = self.outputs_root / job_id
        output_dir.mkdir(parents=True, exist_ok=True)

        await progress_callback("story", "Developing the story with Groq or the offline fallback...", 6)
        story = await self.screenwriter.develop_story(idea, user_requirement)
        (output_dir / "story.txt").write_text(story, encoding="utf-8")

        await progress_callback("script", "Writing two concise scenes...", 15)
        scene_scripts = await self.screenwriter.write_script_based_on_story(story, user_requirement)
        if not scene_scripts:
            scene_scripts = [story]

        await progress_callback("characters", "Building a consistent cast description...", 24)
        characters = await self.character_extractor.extract_characters("\n\n".join(scene_scripts))

        scene_paths = []
        progress_per_scene = max(22, int(58 / max(len(scene_scripts), 1)))
        for index, scene_script in enumerate(scene_scripts):
            scene_dir = output_dir / f"scene_{index:02d}"
            base = 28 + index * progress_per_scene
            scene_path = await self.script2video.run(
                script=scene_script,
                characters=characters,
                user_requirement=user_requirement,
                style=style,
                working_dir=str(scene_dir),
                progress_callback=progress_callback,
                scene_idx=index,
                base_progress=base,
                progress_range=progress_per_scene,
                creator_name=creator_name,
            )
            scene_paths.append(scene_path)

        await progress_callback("concat", "Assembling the final free local MP4...", 92)
        final_path = output_dir / "final_video.mp4"
        await concatenate_videos(scene_paths, str(final_path))
        await progress_callback("complete", "Your Ayett Stories video is ready.", 100)
        return str(final_path)
