import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# Load the .env file next to this script.
load_dotenv(Path(__file__).resolve().parent / ".env", override=True)

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise SystemExit("OPENAI_API_KEY is missing from your .env file.")

client = OpenAI(api_key=api_key)

response = client.responses.create(
    model="gpt-4.1-mini",
    input="Reply with exactly: ScopeGuard API connection successful!",
    max_output_tokens=50,
)

print(response.output_text)