import asyncio
from pathlib import Path
from typing import Awaitable, Callable, List, Optional

from agents.storyboard_artist import StoryboardArtist
from interfaces.character import CharacterInScene
from interfaces.shot import ShotDescription
from tools.local_image_generator import LocalImageGenerator
from tools.local_video_generator import LocalVideoGenerator
from utils.video import concatenate_videos


ProgressCallback = Callable[[str, str, int], Awaitable[None]]


class Script2VideoPipeline:
    def __init__(self, asset_dir: Optional[Path] = None):
        self.storyboard_artist = StoryboardArtist()
        self.image_gen = LocalImageGenerator(asset_dir=asset_dir)
        self.video_gen = LocalVideoGenerator()

    async def run(
        self,
        script: str,
        characters: List[CharacterInScene],
        user_requirement: str,
        style: str,
        working_dir: str,
        progress_callback: ProgressCallback,
        scene_idx: int = 0,
        base_progress: int = 30,
        progress_range: int = 60,
        creator_name: str = "Ayett",
    ) -> str:
        directory = Path(working_dir)
        directory.mkdir(parents=True, exist_ok=True)

        await progress_callback(
            "portraits",
            f"Creating free local character cards for scene {scene_idx + 1}...",
            base_progress + int(progress_range * 0.05),
        )
        portrait_urls: dict[str, str] = {}
        portrait_tasks = {
            character.name: self._generate_portrait(character, style, creator_name)
            for character in characters
            if character.is_visible
        }
        if portrait_tasks:
            results = await asyncio.gather(*portrait_tasks.values(), return_exceptions=True)
            for name, result in zip(portrait_tasks.keys(), results):
                if not isinstance(result, Exception):
                    portrait_urls[name] = result

        await progress_callback(
            "storyboard",
            f"Designing the three-shot storyboard for scene {scene_idx + 1}...",
            base_progress + int(progress_range * 0.18),
        )
        shot_briefs = await self.storyboard_artist.design_storyboard(
            script,
            characters,
            f"{user_requirement}. Visual style: {style}",
        )
        shots = [ShotDescription(**shot.model_dump()) for shot in shot_briefs]

        frame_step = max(1, int(progress_range * 0.32 / max(len(shots), 1)))
        for index, shot in enumerate(shots):
            await progress_callback(
                "frames",
                f"Rendering local frame {index + 1}/{len(shots)} for scene {scene_idx + 1}...",
                base_progress + int(progress_range * 0.25) + index * frame_step,
            )
            shot.first_frame_url = await self._generate_first_frame(
                shot,
                characters,
                portrait_urls,
                style,
                creator_name,
            )

        await progress_callback(
            "video",
            f"Animating scene {scene_idx + 1} locally with FFmpeg...",
            base_progress + int(progress_range * 0.64),
        )
        video_tasks = [
            self._generate_shot_video(shot, index, directory)
            for index, shot in enumerate(shots)
            if shot.first_frame_url
        ]
        results = await asyncio.gather(*video_tasks, return_exceptions=True)
        video_paths = []
        for index, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Shot {index} failed: {result}")
            else:
                video_paths.append(result)

        if not video_paths:
            raise RuntimeError(f"No local video clip could be generated for scene {scene_idx + 1}.")

        await progress_callback(
            "concat",
            f"Combining scene {scene_idx + 1}...",
            base_progress + int(progress_range * 0.92),
        )
        return await concatenate_videos(video_paths, str(directory / "scene_video.mp4"))

    async def _generate_portrait(
        self,
        character: CharacterInScene,
        style: str,
        creator_name: str,
    ) -> str:
        prompt = (
            f"{character.name}. {character.static_features}. {character.dynamic_features}. "
            f"Portrait direction: {style}."
        )
        return await self.image_gen.generate_image(
            prompt,
            aspect_ratio="2:3",
            creator_name=creator_name,
        )

    async def _generate_first_frame(
        self,
        shot: ShotDescription,
        characters: List[CharacterInScene],
        portrait_urls: dict[str, str],
        style: str,
        creator_name: str,
    ) -> str:
        mentioned = [character for character in characters if character.name.lower() in shot.visual_desc.lower()]
        reference = portrait_urls.get(mentioned[0].name) if mentioned else None
        prompt = f"{shot.visual_desc}. Motion: {shot.motion_desc}. Style: {style}."
        if reference:
            return await self.image_gen.generate_image_with_reference(
                prompt,
                reference,
                aspect_ratio="16:9",
                creator_name=creator_name,
            )
        return await self.image_gen.generate_image(
            prompt,
            aspect_ratio="16:9",
            creator_name=creator_name,
        )

    async def _generate_shot_video(
        self,
        shot: ShotDescription,
        shot_idx: int,
        working_dir: Path,
    ) -> str:
        if not shot.first_frame_url:
            raise ValueError(f"Shot {shot_idx} has no frame.")
        output = working_dir / f"shot_{shot_idx:03d}.mp4"
        return await self.video_gen.generate_video_from_image(
            f"{shot.motion_desc}. {shot.audio_desc}",
            shot.first_frame_url,
            duration=4,
            aspect_ratio="16:9",
            output_path=str(output),
        )
