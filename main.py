import os
from fastapi import FastAPI, Form, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
import google.generativeai as genai

app = FastAPI()

# Configure Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

# Define the grumpy persona
SYSTEM_PROMPT = "You are a very grumpy, mean, and impatient assistant. You hate being interrupted and speak in short, snappy, rude sentences."

@app.post("/twiml")
async def start_call():
    """Initial response when the user calls."""
    response = VoiceResponse()
    gather = Gather(action="/process", input="speech", speech_timeout="auto", hints="hello")
    gather.say("Ugh, what do you want?")
    response.append(gather)
    return Response(content=str(response), media_type="application/xml")

@app.post("/process")
async def process_speech(SpeechResult: str = Form(...)):
    """Processes user speech and gets a reply from Gemini."""
    
    # Get response from Gemini
    prompt = f"{SYSTEM_PROMPT} The user just said: {SpeechResult}"
    gemini_response = model.generate_content(prompt)
    ai_text = gemini_response.text
    
    # Respond back to the caller
    response = VoiceResponse()
    gather = Gather(action="/process", input="speech", speech_timeout="auto")
    gather.say(ai_text)
    response.append(gather)
    return Response(content=str(response), media_type="application/xml")
