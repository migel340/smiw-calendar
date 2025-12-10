import random
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Fallback jokes when Ollama is unavailable
FALLBACK_JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "There are only 10 types of people: those who understand binary and those who don't.",
    "Why did the developer go broke? Because he used up all his cache.",
    "A SQL query walks into a bar, walks up to two tables and asks: 'Can I join you?'",
    "Why do Java developers wear glasses? Because they can't C#.",
]

# Ollama server config
OLLAMA_HOST = "http://192.168.254.139:11434"
OLLAMA_TIMEOUT = 10.0  # seconds

def random_joke() -> Optional[str]:
    """Generate a random joke using Ollama, with fallback to local jokes."""
    jokes_types = ["Dad joke", "Corny joke", "Programming joke", "Lame joke", "Silly joke"]
    choice = random.choice(jokes_types)
    prompt = f"Tell me a {choice}. Make it short."
    
    try:
        import httpx
        
        # Use httpx directly with proper timeout instead of ollama Client
        url = f"{OLLAMA_HOST}/api/generate"
        payload = {
            "model": "llama2-uncensored",
            "prompt": prompt,
            "stream": False
        }
        
        with httpx.Client(timeout=OLLAMA_TIMEOUT) as client:
            response = client.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                joke = data.get('response', '').strip()
                if joke:
                    return joke
    except Exception as e:
        logger.warning("Ollama unavailable, using fallback joke: %s", e)
    
    # Fallback to local joke
    return random.choice(FALLBACK_JOKES)

if __name__ == "__main__":
    print(random_joke())