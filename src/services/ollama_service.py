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
OLLAMA_MODEL = "llama2-uncensored"
OLLAMA_TIMEOUT = 10.0  # seconds

def random_joke() -> Optional[str]:
    """Generate a random joke using Ollama, with fallback to local jokes."""
    jokes_types = ["Dad joke", "Corny joke", "Programming joke", "Lame joke", "Silly joke"]
    choice = random.choice(jokes_types)
    prompt = f"Tell me a {choice}. Make it short."
    
    try:
        import ollama
        
        client = ollama.Client(host=OLLAMA_HOST, timeout=OLLAMA_TIMEOUT)
        response = client.generate(
            model=OLLAMA_MODEL,
            prompt=prompt,
        )
        joke = response.get('response', '').strip()
        if joke:
            return joke
    except Exception as e:
        logger.warning("Ollama unavailable, using fallback joke: %s", e)
    
    # Fallback to local joke
    return random.choice(FALLBACK_JOKES)

if __name__ == "__main__":
    print(random_joke())