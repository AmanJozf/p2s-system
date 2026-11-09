import os
from dotenv import load_dotenv
from google import genai

# 1. Load the secret API key from our .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

print(f"Connecting to Gemini API using key: ...{api_key[-6:] if api_key else 'NONE'}")

# 2. Initialize the Google GenAI Client
client = genai.Client(api_key=api_key)

# 3. Test prompt for Problem-to-Service classification
sample_problem = "My landlord hasn't given me my £1200 deposit back and it has been 3 weeks since I moved out."

prompt = f"""
You are the AI triage engine for the Problem-to-Service (P2S) system.
Analyze this user problem:
"{sample_problem}"

Provide a structured response:
1. Primary Category (Housing, IT, or Appliances)
2. Immediate Urgency (Low/Medium/High)
3. One key follow-up question needed to route them to the right service
"""

response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents=prompt,
)

print("\n--- TEST SUCCESSFUL! AI RESPONSE ---")
print(response.text)
