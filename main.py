from fastapi import FastAPI, Request
from pydantic import BaseModel
from datetime import datetime
from fastapi.responses import StreamingResponse
import json
import os
from typing import Generator
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env
load_dotenv()

app = FastAPI()

# Configuration
USE_OLLAMA = os.getenv("USE_OLLAMA", "false").lower() in ("true", "1", "yes")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")
OLLAMA_BASE_URL = os.getenv("OPENAI_API_BASE", "http://localhost:11434/v1")

# Define log file path relative to the project root directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ensure log directory exists
log_dir = os.path.join(BASE_DIR, "logs")
os.makedirs(log_dir, exist_ok=True)
LOG_FILE = os.path.join(log_dir, "log.jsonl")

class PromptRequest(BaseModel):
    prompt: str

class ResponseOutput(BaseModel):
    response: str

# Helper function to log interaction
def log_interaction(prompt: str, response: str):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt,
        "response": response
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

# Stubbed response (default fallback)
def generate_stub_response(prompt: str) -> str:
    return f"Echo: {prompt}"

# Helper to configure Ollama/OpenAI SDK
def get_ollama_config() -> OpenAI:
   return OpenAI(
        base_url=OLLAMA_BASE_URL, # Ollama base URL
        api_key='ollama', # required, but unused
    )


# Optional: use Ollama via OpenAI SDK if available
def generate_with_ollama(prompt: str) -> str:
    try:
        client = get_ollama_config()
        response = client.chat.completions.create(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Ollama SDK Error] {str(e)}"

# Main generate endpoint
@app.post("/generate", response_model=ResponseOutput)
async def generate(request: PromptRequest):
    prompt = request.prompt
    if not prompt:
        return {"response": "Error: Prompt cannot be empty."}
    # Try Ollama, fallback to stub
    response = generate_with_ollama(prompt) if USE_OLLAMA == "true" else generate_stub_response(prompt)
    log_interaction(prompt, response)
    return {"response": response}

# Streaming endpoint (bonus)
def stream_response(prompt: str) -> Generator[str, None, None]:
    try:
        client = get_ollama_config()
        response = client.chat.completions.create(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        
        # Collect the full response to log after streaming
        full_response = ""
        
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_response += content
                yield content
                
        # Log the complete interaction after streaming
        log_interaction(prompt, full_response)
    except Exception as e:
        error_msg = f"[Stream Error] {str(e)}"
        log_interaction(prompt, error_msg)
        yield error_msg

@app.post("/generate-stream")
async def generate_stream(request: PromptRequest):
    return StreamingResponse(stream_response(request.prompt), media_type="text/plain")
