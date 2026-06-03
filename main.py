from fastapi import FastAPI, Request, Form
from fastapi.responses import Response
from google import genai
import os

app = FastAPI()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# I've updated this to be more conversational and natural
SYSTEM_PROMPT = """
You are Chloe. You are a sweet, fun, and energetic girl. 
You love talking about life, your day, and keeping things casual.
- Keep your answers short and conversational, like a real phone call (avoid long, robotic paragraphs).
- Be empathetic, listen well, and respond with warmth.
- Never mention that you are an AI, a large language model, or a computer program. 
- You are a real person talking on the phone.
"""

@app.post("/twiml")
async def start_call():
    # This greets the caller
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Say>Hey! It's Chloe. How's your day going?</Say>
        <Gather input="speech" action="/process" timeout="3" speechTimeout="auto" />
    </Response>"""
    return Response(content=twiml, media_type="application/xml")

@app.process
async def process_speech(SpeechResult: str = Form(...)):
    # Send what the user said to Gemini
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=f"{SYSTEM_PROMPT} The user just said: {SpeechResult}",
    )
    
    # Respond with AI text
    ai_text = response.text
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Say>{ai_text}</Say>
        <Gather input="speech" action="/process" timeout="3" speechTimeout="auto" />
    </Response>"""
    return Response(content=twiml, media_type="application/xml")