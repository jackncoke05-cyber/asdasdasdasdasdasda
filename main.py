import os
from fastapi import FastAPI, Form, Request
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from google import genai

app = FastAPI()

# NEW Gemini client (correct SDK)
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

SYSTEM_PROMPT = """
You are a flirty, slightly sarcastic female AI voice on a phone call.
Keep responses short (1-2 sentences max).
You are natural, human-like, and conversational.
Never mention you are AI.
"""

@app.get("/")
def home():
    return {"status": "running"}

@app.post("/twiml")
async def twiml():
    response = VoiceResponse()

    gather = Gather(
        input="speech",
        action="/process",
        method="POST",
        speech_timeout="auto"
    )

    gather.say("Hello? Who is this?")
    response.append(gather)

    return Response(content=str(response), media_type="application/xml")


@app.post("/process")
async def process(request: Request, SpeechResult: str = Form("")):

    response = VoiceResponse()

    # fallback if nothing heard
    if not SpeechResult:
        response.say("I didn't hear anything.")
        response.redirect("/twiml")
        return Response(str(response), media_type="application/xml")

    prompt = f"{SYSTEM_PROMPT}\nUser said: {SpeechResult}"

    try:
        result = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        ai_text = result.text
    except Exception as e:
        print("Gemini error:", e)
        ai_text = "I'm having issues right now."

    gather = Gather(
        input="speech",
        action="/process",
        method="POST",
        speech_timeout="auto"
    )

    gather.say(ai_text, voice="alice")
    response.append(gather)

    return Response(str(response), media_type="application/xml")
