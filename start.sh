#!/bin/bash

echo "🚀 Avvio DocPilot..."
echo "================================"

# Colori
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_DIR="/Users/paulblack/Desktop/Development/DocPilot"

# 1. Backend
echo -e "${YELLOW}▶ Avvio Backend FastAPI...${NC}"
osascript -e "tell application \"Terminal\" to do script \"cd $PROJECT_DIR/backend && source .venv/bin/activate && uvicorn main:app --reload --port 8000 --host 0.0.0.0\""
sleep 2
echo -e "${GREEN}✓ Backend avviato su http://localhost:8000${NC}"

# 2. Frontend
echo -e "${YELLOW}▶ Avvio Frontend...${NC}"
osascript -e "tell application \"Terminal\" to activate" -e "tell application \"Terminal\" to do script \"npx serve $PROJECT_DIR/frontend -p 3000 -c $PROJECT_DIR/frontend/serve.json\""
sleep 2
echo -e "${GREEN}✓ Frontend avviato su http://localhost:3000${NC}"

# 3. n8n Docker
echo -e "${YELLOW}▶ Avvio n8n...${NC}"
docker start n8n 2>/dev/null && echo -e "${GREEN}✓ n8n avviato su http://localhost:5678${NC}" || echo -e "${RED}✗ n8n non trovato — avvialo manualmente${NC}"
sleep 2

# 4. Cloudflare Tunnel
echo -e "${YELLOW}▶ Avvio Cloudflare Tunnel...${NC}"
osascript -e "tell application \"Terminal\" to do script \"cloudflared tunnel --url http://localhost:5678\""
sleep 3
echo -e "${GREEN}✓ Cloudflare Tunnel avviato${NC}"

echo ""
echo "================================"
echo -e "${GREEN}✅ DocPilot avviato!${NC}"
echo ""
echo "📌 URL utili:"
echo "   Frontend  → http://localhost:3000"
echo "   Backend   → http://localhost:8000"
echo "   API Docs  → http://localhost:8000/docs"
echo "   n8n       → http://localhost:5678"
echo ""
echo -e "${YELLOW}⚠️  Ricorda: copia il nuovo URL di Cloudflare e aggiornalo su GitHub → Webhooks${NC}"
echo "================================"

# Apri il frontend nel browser
sleep 2
open "http://localhost:3000"
