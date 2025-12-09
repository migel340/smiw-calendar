import random
from typing import Optional
from ollama import Client
import httpx

def random_joke() -> Optional[str]:
    jokes = ["Dad joke", "Corny joke", "Programming joke", "Lame joke", "Silly joke", "Stale joke", "Dry joke"]
    choice = random.choice(jokes)
    prompt = f"Tell me a {choice}. Make it short."
    client = Client(
        host="http://192.168.254.139:11434",
        transport=httpx.HTTPTransport(retries=3)
    )
    result = client.generate(model='llama2-uncensored', prompt=prompt)
    return result['response']

if __name__ == "__main__":
    print(random_joke())