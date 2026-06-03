import os
from fastapi import FastAPI, Form, Request
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from google import genai

app = FastAPI()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

SYSTEM_PROMPT = """
You are a flirty, slightly sarcastic female on a phone call.
Keep responses short and natural.
Never mention that you are AI.
"""

@app.get("/")
def home():
    return {"status": "running"}

@app.post("/twiml")
async def twiml():
    response = VoiceResponse()

    gather = Gather(
        input="speech",
        action="https://YOUR-RENDER-URL.onrender.com/process",
        method="POST",
        speech_timeout="auto"
    )

    gather.say("Hello. Who is this?")
    response.append(gather)

    return Response(
        content=str(response),
        media_type="application/xml"
    )

@app.post("/process")
async def process(request: Request, SpeechResult: str = Form("")):
    response = VoiceResponse()

    print("SpeechResult:", SpeechResult)

    if not SpeechResult:
        response.say("I didn't catch that.")
        response.redirect("https://YOUR-RENDER-URL.onrender.com/twiml")
        return Response(
            content=str(response),
            media_type="application/xml"
        )

    prompt = f"{SYSTEM_PROMPT}\nUser said: {SpeechResult}"

    try:
        result = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        ai_text = (result.text or "").strip()

        if not ai_text:
            ai_text = "Could you say that again?"

    except Exception as e:
        print("Gemini error:", e)
        ai_text = "Sorry, I'm having trouble right now."

    print("AI Response:", ai_text)

    response.say(ai_text, voice="alice")

    gather = Gather(
        input="speech",
        action="https://YOUR-RENDER-URL.onrender.com/process",
        method="POST",
        speech_timeout="auto"
    )

    response.append(gather)

    return Response(
        content=str(response),
        media_type="application/xml"
    )
