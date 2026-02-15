# Real-Time Voice AI Agent with RAG

A voice AI agent that lets you upload documents (PDF/TXT) and have real-time voice conversations grounded in those documents. Built with FastAPI, React, LiveKit (WebRTC), OpenAI, and ChromaDB.

Upload a product manual, research paper, or any text — then ask questions by voice. The agent retrieves relevant context from your documents and speaks the answer back.

## Architecture

```
Frontend (React :3000)  ──HTTP/WebRTC──▶  Backend (FastAPI :8000)
                                              │
                              ┌───────────────┼───────────────┐
                              ▼               ▼               ▼
                         LiveKit Server   ChromaDB        OpenAI API
                         (WebRTC)         (Vector Store)  (STT/LLM/TTS)
```

**Data flow:** Upload → text extraction → chunking → embedding → ChromaDB. Voice input → STT (Whisper) → RAG retrieval → LLM (GPT-4) with context → TTS → audio response.

## Features

- **Real-time voice conversation** — WebRTC-based low-latency voice via LiveKit
- **RAG over uploaded documents** — upload PDFs or TXT files, agent answers using their content
- **Editable system prompt** — customize agent personality and behavior on the fly
- **Live transcription** — see both your speech and agent responses in real-time
- **RAG source panel** — view which document chunks were used for each answer
- **Mic controls** — mute/unmute during conversation

## Prerequisites

- OpenAI API key ([platform.openai.com](https://platform.openai.com))
- LiveKit Cloud account ([cloud.livekit.io](https://cloud.livekit.io)) — free tier works

**For Docker setup:**
- Docker & Docker Compose

**For manual setup:**
- Python 3.10+
- Node.js 18+

## Getting Started

### 1. Clone and configure

```bash
git clone <your-repo-url>
cd voice-ai-agent
cp .env.example .env
```

Edit `.env` with your credentials:

```env
OPENAI_API_KEY=sk-your-openai-api-key-here
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your-livekit-api-key
LIVEKIT_API_SECRET=your-livekit-api-secret
```

### 2a. Run with Docker (recommended)

```bash
docker-compose up --build
```

That's it. Frontend runs on `http://localhost:3000`, backend on `http://localhost:8000`.

```bash
# Useful commands
docker-compose logs -f backend     # Tail backend logs
docker-compose down                # Stop everything
```

### 2b. Run manually (development)

**Backend:**

```bash
cd backend
python -m venv venv
source venv/bin/activate           # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend** (in a separate terminal):

```bash
cd frontend
npm install
npm start                          # Dev server on http://localhost:3000
```

Or use the helper scripts:

```bash
./setup.sh          # Docker-based setup
./run-manual.sh     # Manual development setup
```

## Usage

1. **Upload documents** — click "Upload Document" and select PDF or TXT files. They get chunked and embedded automatically.
2. **Set a system prompt** — customize how the agent behaves (e.g. "You are a product support specialist. Answer using the uploaded documentation.")
3. **Connect** — click "Connect to Agent" and allow microphone access.
4. **Talk** — ask questions. The agent retrieves relevant chunks from your documents and responds by voice.
5. **Check sources** — the RAG Sources panel shows which document sections were used.

## Project Structure

```
voice-ai-agent/
├── backend/
│   ├── main.py                 # FastAPI entry point, CORS, routers
│   ├── voice_agent.py          # LiveKit voice agent (STT → LLM → TTS + RAG)
│   ├── dependencies.py         # Service singletons, shared state
│   ├── database.py             # SQLite persistence
│   ├── documents/              # Document upload & processing
│   ├── rag/                    # RAG retrieval service
│   ├── prompt/                 # System prompt management
│   ├── livekit_auth/           # LiveKit token generation
│   ├── health/                 # Health check endpoint
│   ├── voice/                  # Voice pipeline (stt.py, llm.py, tts.py)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.js              # Root component
│   │   ├── components/
│   │   │   ├── KnowledgeBase/  # Document upload & list
│   │   │   ├── AgentConfig/    # System prompt editor
│   │   │   ├── VoiceConversation/  # LiveKit room wrapper
│   │   │   ├── VoiceAssistantUI/   # Transcript + RAG sources
│   │   │   ├── AlertMessage/   # Error/success alerts
│   │   │   └── Instructions/   # Usage guide
│   │   ├── hooks/              # useDocuments, usePrompt, useVoiceConnection
│   │   └── services/           # Axios API client
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React, LiveKit React SDK, CSS Modules, Axios |
| Backend | FastAPI, LiveKit Agents SDK, LangChain |
| Voice | OpenAI Whisper (STT), GPT-4 (LLM), OpenAI TTS |
| Vector DB | ChromaDB |
| Transport | WebRTC via LiveKit |
| Storage | SQLite (metadata), ChromaDB (embeddings) |

## API Endpoints

Swagger docs at `http://localhost:8000/docs` when running.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/upload-document` | Upload and process a PDF/TXT file |
| `GET` | `/documents` | List uploaded documents |
| `DELETE` | `/documents/{filename}` | Delete a document |
| `POST` | `/query` | Test RAG retrieval |
| `GET` | `/prompt` | Get current system prompt |
| `POST` | `/prompt` | Update system prompt |
| `POST` | `/generate-token` | Generate LiveKit access token |

## Configuration

All configuration is via `.env`. Key settings:

```env
# Voice pipeline models
STT_MODEL=whisper-1
LLM_MODEL=gpt-4
TTS_MODEL=tts-1
TTS_VOICE=alloy

# RAG tuning
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=3
```

## Limitations

- **Document size** — max 10MB per file
- **File formats** — PDF and TXT only
- **Single room** — one LiveKit voice room at a time (no multi-user concurrency)
- **English only** — STT and TTS are configured for English
- **No auth** — no user authentication; designed for local/demo use
- **SQLite** — metadata stored in SQLite (`app.db`), not suited for horizontal scaling

## Tradeoffs

| Decision | Why | Downside |
|----------|-----|----------|
| ChromaDB (in-process) | Zero infrastructure, just works | Not horizontally scalable; data lives on disk in `chroma_db/` |
| OpenAI for all AI (STT + LLM + TTS) | Consistent API, easy setup | Vendor lock-in, API costs, latency depends on OpenAI |
| LiveKit Cloud | Managed WebRTC, no TURN/STUN setup | Requires external account; adds a network hop |
| SQLite for metadata | No extra database to run | Single-writer, no concurrent access |
| `window.confirm` for delete | Simple, no extra UI library needed | Not styleable, looks different per browser |
| No authentication | Keeps demo simple | Not production-safe as-is |

## Troubleshooting

**LiveKit connection fails**
- Verify `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET` in `.env`
- Make sure your LiveKit Cloud project is active
- Check browser supports WebRTC (Chrome/Firefox/Edge)

**Document upload fails**
- Only `.pdf` and `.txt` are accepted, max 10MB
- Check that `OPENAI_API_KEY` is valid (embeddings need it)
- Check backend logs: `docker-compose logs -f backend`

**Agent not responding**
- Allow microphone permission in your browser
- Check OpenAI API quota is not exhausted
- Verify backend is running: `curl http://localhost:8000/health`

**Microphone not working**
- Try a different browser
- Check system audio settings
- Make sure no other app is using the mic

## License

MIT
