# MiniVault API

A lightweight local REST API that simulates a prompt/response system using FastAPI and optionally a local LLM via Ollama (OpenAI-compatible SDK).

---

## Local Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the API
```bash
uvicorn main:app --reload
```

---

## Docker Setup (without Ollama)

### 1. Build the Docker image
```bash
docker build -t minivault-api .
```

### 2. Run the container
```bash
docker run -p 8000:8000 --env-file .env minivault-api
```

### Optional: Mount volume for logs
```bash
docker run -p 8000:8000 -v $(pwd)/logs:/app/logs --env-file .env minivault-api
```

---

## Docker Compose Setup (API + Ollama)

### 1. Run both services
```bash
docker-compose up --build
```

This runs:
- `ollama` as a local LLM backend
- `minivault-api` as your FastAPI server

Ollama will download the model on first use.

---

## .env Configuration (Example)
```env
USE_OLLAMA=1
OLLAMA_MODEL=llama3
OPENAI_API_BASE=http://ollama:11434/v1
```

---

## API Endpoints

### POST `/generate`
Input:
```json
{ "prompt": "Hello there" }
```
Output:
```json
{ "response": "..." }
```

### POST `/generate-stream`
Streams token-by-token response.

---

## CLI Usage

### Run from terminal
```bash
python cli.py "Hello from CLI"
python cli.py "Stream this message" --stream
```

Make sure `.env` includes:
```env
API_URL=http://localhost:8000
```

---

## Project Structure
```
minivault-api/
├── main.py                # FastAPI app
├── cli.py                 # Command-line interface for testing
├── utils.py               # Helper functions
├── logs/log.jsonl         # Local logs
├── requirements.txt       # Python dependencies
├── .env                   # Environment config
├── Dockerfile             # Docker build instructions
├── .dockerignore          # Docker ignore rules
├── docker-compose.yml     # Docker Compose for API + Ollama
└── README.md              # Project guide
```

---

## Notes & Tradeoffs
- Uses `openai.ChatCompletion` with local Ollama for LLM response.
- Stub fallback enabled if Ollama not available.
- Token streaming supported.
- Logging all prompts/responses to `logs/log.jsonl`.
