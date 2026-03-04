import os

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY is None:
    print("WARNING: GEMINI_API_KEY is not set!")