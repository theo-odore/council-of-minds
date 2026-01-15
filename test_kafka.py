import requests
import json

OLLAMA_API = "http://localhost:11434/api/generate"

payload = {
    "model": "qwen",
    "prompt": "You are Kafka. Murmur a pessimistic observation. Keep it concise.",
    "stream": False
}

print(f"Testing model: {payload['model']}...")
try:
    response = requests.post(OLLAMA_API, json=payload)
    response.raise_for_status()
    result = response.json()
    print("Response received:")
    print(result.get("response"))
except Exception as e:
    print(f"Error: {e}")
