import requests, os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

key = os.getenv("FIREFLIES_API_KEY")
if not key:
    print("ERROR: Key not found in .env")
    exit(1)

r = requests.post(
    "https://api.fireflies.ai/graphql",
    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    json={"query": "{ transcripts(limit: 3) { id title date } }"},
    timeout=15
)
data = r.json()
if "errors" in data:
    print("ERROR:", data["errors"][0]["message"])
else:
    transcripts = data.get("data", {}).get("transcripts", [])
    print(f"Fireflies connected — found {len(transcripts)} recent transcript(s)")
    for t in transcripts:
        print(f"  {t.get('date', '?')} — {t.get('title', 'Untitled')}")
