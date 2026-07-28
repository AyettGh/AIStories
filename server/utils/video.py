import asyncio
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List

import httpx
import imageio_ffmpeg


async def download_video(url: str, dest_path: str) -> str:
    """Download a video URL or copy a local video to the requested path."""
    source = Path(url)
    if source.exists():
        Path(dest_path).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest_path)
        return dest_path

    async with httpx.AsyncClient(timeout=120, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()
        Path(dest_path).parent.mkdir(parents=True, exist_ok=True)
        Path(dest_path).write_bytes(response.content)
    return dest_path


async def concatenate_videos(video_paths: List[str], output_path: str) -> str:
    if not video_paths:
        raise ValueError("No video clips to concatenate")

    paths = [Path(path).resolve() for path in video_paths]
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing video clips: {missing}")

    target = Path(output_path).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)

    if len(paths) == 1:
        shutil.copyfile(paths[0], target)
        return str(target)

    await asyncio.to_thread(_concat_ffmpeg, paths, target)
    return str(target)


def _concat_ffmpeg(paths: List[Path], target: Path) -> None:
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    list_file = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8")
    try:
        for path in paths:
            escaped = str(path).replace("'", "'\\''")
            list_file.write(f"file '{escaped}'\n")
        list_file.close()

        copy_command = [
            ffmpeg,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            list_file.name,
            "-c",
            "copy",
            "-movflags",
            "+faststart",
            str(target),
        ]
        result = subprocess.run(copy_command, capture_output=True, text=True)
        if result.returncode == 0:
            return

        # Reliable fallback if stream-copy concatenation is rejected.
        command = [ffmpeg, "-y"]
        for path in paths:
            command.extend(["-i", str(path)])
        inputs = "".join(f"[{idx}:v:0]" for idx in range(len(paths)))
        filter_complex = f"{inputs}concat=n={len(paths)}:v=1:a=0[outv]"
        command.extend(
            [
                "-filter_complex",
                filter_complex,
                "-map",
                "[outv]",
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
                str(target),
            ]
        )
        fallback = subprocess.run(command, capture_output=True, text=True)
        if fallback.returncode != 0:
            raise RuntimeError(f"Video concatenation failed: {fallback.stderr[-1200:]}")
    finally:
        Path(list_file.name).unlink(missing_ok=True)
