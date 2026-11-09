"""Probe which Gemini models the current API key can actually call, with latency."""
import os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options=types.HttpOptions(timeout=45_000),  # ms; don't hang on a slow model
)

CANDIDATES = sys.argv[1:] or [
    "gemini-3.1-pro-preview", "gemini-pro-latest", "gemini-3.8-flash",
    "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash",
    "gemini-3.1-flash-lite", "gemini-3.5-flash-lite",
    "gemini-2.5-pro", "gemini-2.5-flash",
]

for m in CANDIDATES:
    t = time.time()
    try:
        r = client.models.generate_content(
            model=m,
            contents='Return JSON {"ok": true, "city": "Berlin"}',
            config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.2),
        )
        print(f"OK   {m:28s} {time.time()-t:5.1f}s  {r.text.strip()[:40]!r}")
    except Exception as e:
        print(f"FAIL {m:28s} {time.time()-t:5.1f}s  {str(e)[:100]}")
    time.sleep(1)
