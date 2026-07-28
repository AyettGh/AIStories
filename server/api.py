import asyncio
import json
import uuid
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from agents.character_extractor import CharacterExtractor
from pipelines.idea2video import Idea2VideoPipeline
from pipelines.script2video import Script2VideoPipeline


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
OUTPUTS_DIR = BASE_DIR / "outputs"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Ayett Stories API", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/outputs", StaticFiles(directory=str(OUTPUTS_DIR)), name="outputs")

jobs: Dict[str, Dict[str, Any]] = {}


class GenerateRequest(BaseModel):
    idea: str = Field(min_length=3, max_length=3000)
    user_requirement: str = Field(default="", max_length=3000)
    style: str = Field(default="Editorial", max_length=60)
    mode: str = Field(default="idea2video", pattern="^(idea2video|script2video)$")
    script: str = Field(default="", max_length=12000)
    creator_name: str = Field(default="Ayett", min_length=1, max_length=60)


class GenerateResponse(BaseModel):
    job_id: str


class JobResult(BaseModel):
    job_id: str
    status: str
    video_url: str | None = None
    error: str | None = None


async def run_pipeline(job_id: str, request: GenerateRequest) -> None:
    job = jobs[job_id]

    async def progress_callback(stage: str, message: str, progress: int) -> None:
        event = {
            "type": "progress",
            "stage": stage,
            "message": message,
            "progress": max(0, min(100, progress)),
        }
        job["events"].append(event)

    try:
        if request.mode == "script2video":
            script = request.script.strip() or request.idea.strip()
            extractor = CharacterExtractor()
            await progress_callback("characters", "Reading the cast from your script...", 8)
            characters = await extractor.extract_characters(script)

            pipeline = Script2VideoPipeline(asset_dir=OUTPUTS_DIR / "generated_assets")
            video_path = await pipeline.run(
                script=script,
                characters=characters,
                user_requirement=request.user_requirement,
                style=request.style,
                working_dir=str(OUTPUTS_DIR / job_id / "scene_00"),
                progress_callback=progress_callback,
                scene_idx=0,
                base_progress=12,
                progress_range=82,
                creator_name=request.creator_name,
            )
            final_path = OUTPUTS_DIR / job_id / "final_video.mp4"
            final_path.parent.mkdir(parents=True, exist_ok=True)
            if Path(video_path).resolve() != final_path.resolve():
                final_path.write_bytes(Path(video_path).read_bytes())
            video_path = str(final_path)
        else:
            pipeline = Idea2VideoPipeline(outputs_root=OUTPUTS_DIR)
            video_path = await pipeline.run(
                idea=request.idea,
                user_requirement=request.user_requirement,
                style=request.style,
                job_id=job_id,
                progress_callback=progress_callback,
                creator_name=request.creator_name,
            )

        relative = Path(video_path).resolve().relative_to(OUTPUTS_DIR.resolve())
        video_url = f"/outputs/{relative.as_posix()}"
        job["status"] = "completed"
        job["video_url"] = video_url
        event = {"type": "complete", "video_url": video_url, "progress": 100}
        job["events"].append(event)
    except Exception as exc:
        message = str(exc)
        job["status"] = "failed"
        job["error"] = message
        event = {"type": "error", "message": message, "progress": -1}
        job["events"].append(event)


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "service": "ayett-stories-api",
        "text_provider": "groq-with-offline-fallback",
        "media_provider": "local-pillow-ffmpeg",
        "paid_media_api_required": False,
    }


@app.post("/api/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "status": "running",
        "events": [],
        "video_url": None,
        "error": None,
    }
    background_tasks.add_task(run_pipeline, job_id, request)
    return GenerateResponse(job_id=job_id)


@app.get("/api/status/{job_id}")
async def status_stream(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    job = jobs[job_id]

    async def event_generator():
        sent = 0
        while True:
            while sent < len(job["events"]):
                event = job["events"][sent]
                sent += 1
                yield f"data: {json.dumps(event)}\n\n"
            if job["status"] in {"completed", "failed"}:
                break
            await asyncio.sleep(0.2)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/result/{job_id}", response_model=JobResult)
async def get_result(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    job = jobs[job_id]
    return JobResult(
        job_id=job_id,
        status=job["status"],
        video_url=job.get("video_url"),
        error=job.get("error"),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
