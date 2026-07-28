import asyncio
import shlex
import subprocess
import uuid
from pathlib import Path
from typing import Optional

import imageio_ffmpeg


class LocalVideoGenerator:
    """Turns a local frame into a short MP4 using free local FFmpeg."""

    def __init__(self):
        self.ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    async def generate_video_from_image(
        self,
        prompt: str,
        image_url: str,
        duration: int = 4,
        aspect_ratio: str = "16:9",
        output_path: Optional[str] = None,
    ) -> str:
        image_path = Path(image_url)
        if not image_path.exists():
            raise FileNotFoundError(f"Frame not found: {image_path}")

        target = Path(output_path or image_path.with_name(f"clip_{uuid.uuid4().hex}.mp4"))
        target.parent.mkdir(parents=True, exist_ok=True)
        await asyncio.to_thread(self._render, image_path, target, max(2, min(duration, 8)))
        return str(target)

    def _render(self, image_path: Path, output_path: Path, duration: int) -> None:
        fps = 25
        frames = duration * fps
        fade_out_start = max(0.8, duration - 0.7)
        video_filter = (
            "scale=1280:720:force_original_aspect_ratio=increase,"
            "crop=1280:720,"
            f"zoompan=z='min(zoom+0.0012,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1280x720:fps={fps},"
            "fade=t=in:st=0:d=0.35,"
            f"fade=t=out:st={fade_out_start}:d=0.65,"
            "format=yuv420p"
        )
        command = [
            self.ffmpeg,
            "-y",
            "-loop",
            "1",
            "-i",
            str(image_path),
            "-vf",
            video_filter,
            "-t",
            str(duration),
            "-r",
            str(fps),
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-movflags",
            "+faststart",
            "-pix_fmt",
            "yuv420p",
            str(output_path),
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Local FFmpeg video generation failed: {result.stderr[-1200:]}")
