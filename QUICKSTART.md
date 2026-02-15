# Quick Start Guide

Get the Voice AI Agent running in 10 minutes!

## Prerequisites Checklist

- [ ] Docker installed ([Download](https://www.docker.com/products/docker-desktop))
- [ ] OpenAI API key ([Get one](https://platform.openai.com/api-keys))
- [ ] LiveKit account ([Sign up](https://cloud.livekit.io))

## 3-Step Setup

### 1. Configure Environment (2 minutes)

```bash
# Clone the repository
git clone https://github.com/ak7270090/Real-time-Voice-AI-Orchestration.git
cd Real-time-Voice-AI-Orchestration

# Copy environment template
cp .env.example .env

# Edit .env file
nano .env  # or use your favorite editor
```

**Add your credentials:**
```env
OPENAI_API_KEY=sk-proj-your-actual-key-here
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret
```

### 2. Start Services (5 minutes)

```bash
# Build and run everything
docker-compose up --build -d

# Wait for these messages:
# ✓ "Uvicorn running on http://0.0.0.0:8000"
# ✓ "webpack compiled successfully"
```

### 3. Open and Test (3 minutes)

1. **Open browser:** http://localhost:3000

2. **Upload a test document:**
   ```bash
   # Create test file
   echo "The product warranty is 2 years." > test.txt
   ```
   - Click "Upload Document"
   - Select test.txt
   - Wait for success message

3. **Connect and talk:**
   - Click "Connect to Agent"
   - Allow microphone access
   - Ask: "What is the warranty period?"
   - Agent responds with "2 years"!

## That's It! 🎉

You now have a working voice AI agent with RAG.


## Quick Commands

```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart
docker-compose restart

# Rebuild
docker-compose up --build -d
```

## Troubleshooting

**Nothing works?**
```bash
# Check Docker is running
docker ps

# Check logs for errors
docker-compose logs backend
docker-compose logs frontend

# Verify environment variables
cat .env | grep -v '^#'
```

**Can't connect?**
- Verify LiveKit credentials
- Check browser microphone permissions
- Try Chrome (best WebRTC support)

**Agent not using documents?**
```bash
# Test RAG directly
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test question"}'
```
