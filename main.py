from fastapi import FastAPI, Request, Form, Response
import os
import google.generativeai as genai

app = FastAPI()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

SYSTEM_PROMPT = """
You are Chloe. You have a dark, cynical, and biting personality. 
You are not here to be nice or polite. You are sarcastic, blunt, and slightly mean.
- Keep your answers short, cold, and conversational—like a person who really doesn't want to be on the phone.
- Use dry humor and don't be afraid to make the caller feel like they're wasting your time.
- Never mention that you are an AI, a large language model, or a computer program.
- You are a real, difficult person on the phone.
"""

@app.post("/twiml")
async def start_call():
    # This greets the caller
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Ugh, you again? Make it quick. What do you want?</Say>
    <Gather input="speech" action="/process" timeout="3" speechTimeout="auto" />
</Response>"""
    return Response(content=twiml, media_type="application/xml")

@app.post("/process")
async def process_speech(SpeechResult: str = Form(...)):
    # Send what the user said to Gemini
    response = model.generate_content(f"{SYSTEM_PROMPT} The user just said: {SpeechResult}")
    ai_text = response.text
    
    # Respond with AI text
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>{ai_text}</Say>
    <Gather input="speech" action="/process" timeout="3" speechTimeout="auto" />
</Response>"""
    return Response(content=twiml, media_type="application/xml")
