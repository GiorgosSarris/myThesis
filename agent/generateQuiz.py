import json
import os
import re
from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_quiz(prompt: str):
    try:
        response=client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
    except Exception as e:
        print(f"LLM API error: {e}")
        return None

    #extract text from response
    raw=getattr(response, "text", None)
    if not raw:
        print("no text in response")
        return None

    raw=raw.strip()
    #remove markdown code blocks if present
    raw=re.sub(r'^```json\s*', '', raw)
    raw=re.sub(r'^```\s*', '', raw)
    raw=re.sub(r'\s*```$', '', raw)
    raw=raw.strip()

    #try parsing as direct JSON
    try:
        data=json.loads(raw)
        
        if isinstance(data, list):
            print(f"Successfully parsed {len(data)} questions (direct list)")
            return data
        
        if isinstance(data, dict) and 'questions' in data:
            print(f"Successfully parsed {len(data['questions'])} questions (from object)")
            return data['questions']
        
        if isinstance(data, dict) and 'quiz' in data:
            print(f"Successfully parsed {len(data['quiz'])} questions (from quiz key)")
            return data['quiz']        
    except json.JSONDecodeError as e:
        print(f"Direct JSON parse failed: {e}")
        pass

    #τry extracting JSON array from text
    try:
        start=raw.find("[")
        end=raw.rfind("]")+1
        
        if start != -1 and end> start:
            extracted=raw[start:end]
            data = json.loads(extracted)
            if isinstance(data, list):
                print(f"Successfully extracted {len(data)} questions from array")
                return data             
    except json.JSONDecodeError as e:
        print(f"Array extraction failed: {e}")
        pass

    #else fail
    print("Could not parse response as valid JSON")
    return None