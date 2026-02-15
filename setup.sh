#!/bin/bash

# Voice AI Agent Setup Script

echo "=================================="
echo "Voice AI Agent - Setup Script"
echo "=================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo ".env file created"
    echo ""
    echo "IMPORTANT: Please edit .env and add your:"
    echo "   - OpenAI API Key"
    echo "   - LiveKit credentials (from cloud.livekit.io)"
    echo ""
    echo "Press Enter when you've updated .env file..."
    read
fi

# Check for required environment variables
source .env

if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "sk-your-openai-api-key-here" ]; then
    echo "Error: OPENAI_API_KEY not set in .env"
    echo "   Get your API key from: https://platform.openai.com/api-keys"
    exit 1
fi

if [ -z "$LIVEKIT_URL" ] || [ "$LIVEKIT_URL" = "wss://your-project.livekit.cloud" ]; then
    echo "Error: LIVEKIT_URL not set in .env"
    echo "   Get your LiveKit credentials from: https://cloud.livekit.io"
    exit 1
fi

echo "Environment variables configured"
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    echo "   Install from: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed"
    echo "   Install from: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "Docker and Docker Compose found"
echo ""

# Build and start services
echo "Building and starting services..."
echo ""

docker-compose pull
docker-compose up -d

echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Services are now running:"
echo "  • Frontend:    http://localhost:3000"
echo "  • Backend:     http://localhost:8000"
echo "  • API Docs:    http://localhost:8000/docs"
echo "  • Voice Agent: running (LiveKit worker)"
echo ""
echo "View logs:"
echo "  docker-compose logs -f"
echo ""
echo "Stop services:"
echo "  docker-compose down"
echo ""
echo "=================================="
