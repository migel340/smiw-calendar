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

def random_joke() -> Optional[str]:
    """Generate a random joke using Ollama, with fallback to local jokes."""
    jokes_types = ["Dad joke", "Corny joke", "Programming joke", "Lame joke", "Silly joke"]
    choice = random.choice(jokes_types)
    prompt = f"Tell me a {choice}. Make it short."
    
    try:
        import httpx
        from ollama import Client
        
        client = Client(
            host="http://192.168.254.139:11434",
            transport=httpx.HTTPTransport(retries=1),
        )
        # Use short timeout to avoid blocking
        result = client.generate(model='llama2-uncensored', prompt=prompt, options={"timeout": 10})
        response = result.get('response', '').strip()
        if response:
            return response
    except Exception as e:
        logger.warning("Ollama unavailable, using fallback joke: %s", e)
    
    # Fallback to local joke
    return random.choice(FALLBACK_JOKES)

if __name__ == "__main__":
    print(random_joke())