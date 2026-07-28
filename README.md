# AI Stories

A personalized micro-drama generator with a light Spotify-inspired interface.

The project turns an idea or a short script into a small motion-comic MP4. It was rebuilt to remove the original paid MuAPI dependency.

## Free architecture

- **Text:** Groq API through its OpenAI-compatible chat endpoint.
- **No Groq key:** deterministic offline story, character, and storyboard fallbacks keep the application working.
- **Images:** generated locally with Pillow as branded editorial story cards.
- **Video:** animated and assembled locally with FFmpeg through `imageio-ffmpeg`.
- **Frontend:** Next.js 14, React, Tailwind CSS, and Lucide icons.
- **Backend:** FastAPI and Pydantic.

No paid image-generation or video-generation API is required.

## Features

- Idea-to-video and script-to-video modes.
- Personalized creator credit,
- Light green, white, grey, and black visual palette.
- Live pipeline progress using Server-Sent Events.
- Story, cast, storyboard, frame, animation, and export stages.
- Downloadable local MP4 result.
- Graceful offline fallback when `GROQ_API_KEY` is missing or unavailable.

## Project structure

```text
AI-Stories/
├── client/                  # Next.js frontend
│   ├── app/
│   └── components/
├── server/                  # FastAPI backend
│   ├── agents/              # Story, character and storyboard agents
│   ├── pipelines/           # Idea-to-video and script-to-video flows
│   ├── tools/               # Groq, Pillow and FFmpeg adapters
│   └── outputs/             # Generated files, created automatically
├── run_windows.bat
└── run_linux.sh
```

## Run on Windows

### 1. Backend

```bat
cd server
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn api:app --reload --port 8000
```

### 2. Frontend

Open a second terminal:

```bat
cd client
npm install
npm run dev
```

Open `http://localhost:3000`.

The included `run_windows.bat` opens both development servers after dependencies have been installed.

## Run on Linux or macOS

```bash
cd server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn api:app --reload --port 8000
```

In a second terminal:

```bash
cd client
npm install
npm run dev
```

## Optional Groq setup

The application works without a key, but a free Groq key gives more original story writing.

Create `server/.env` from `.env.example`:

```env
GROQ_API_KEY=your_key_here
GROQ_MODEL=openai/gpt-oss-20b
```

Groq exposes an OpenAI-compatible endpoint at `https://api.groq.com/openai/v1/chat/completions`. Active model names can change, so update `GROQ_MODEL` using Groq's current supported-model list when necessary.

## API

- `GET /api/health`
- `POST /api/generate`
- `GET /api/status/{job_id}`
- `GET /api/result/{job_id}`
- Generated media: `/outputs/...`

Example generation request:

```json
{
  "mode": "idea2video",
  "idea": "A student discovers an old voice note before her final presentation.",
  "script": "",
  "user_requirement": "Hopeful ending and two short scenes",
  "style": "Editorial",
  "creator_name": "AI"
}
```

## Important output note

The free local media pipeline produces a clean **motion-comic / animated story-card video**, not photorealistic text-to-video footage. This choice makes the project predictable, private, and testable without paid APIs or a GPU.
