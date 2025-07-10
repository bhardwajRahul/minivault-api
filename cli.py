import requests
import argparse
import os
# cli.py - Command Line Interface for MiniVault API

API_URL = "http://localhost:8000"

def call_generate(prompt: str, stream: bool = False):
    endpoint = f"{API_URL}/generate-stream" if stream else f"{API_URL}/generate"
    response = requests.post(endpoint, json={"prompt": prompt}, stream=stream)

    if response.status_code != 200:
        print("Error:", response.status_code, response.text)
        return

    if stream:
        for chunk in response.iter_content(chunk_size=1024):
            print(chunk.decode(), end="", flush=True)
        print()
    else:
        print("Response:", response.json()["response"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MiniVault API CLI")
    parser.add_argument("prompt", type=str, help="Prompt to send")
    parser.add_argument("--stream", action="store_true", help="Use streaming endpoint")

    args = parser.parse_args()
    call_generate(args.prompt, args.stream)
