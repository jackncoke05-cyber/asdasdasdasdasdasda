import os
import traceback

from fastapi import FastAPI, Form, Request
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Gather, Pause
from google import genai

app = FastAPI()

# Gemini client
client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)

SYSTEM_PROMPT = """
You are a flirty, slightly sarcastic female on a phone call.
Keep responses under 15 words.
Be natural and conversational.
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
        action="https://asdasdasdasdasdasda-1.onrender.com/process",
        method="POST",
        speech_timeout="2"
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

    print("================================")
    print("SpeechResult:", SpeechResult)
    print("================================")

    if not SpeechResult:
        response.say("I didn't catch that.")

        response.redirect(
            "https://asdasdasdasdasdasda-1.onrender.com/twiml"
        )

        return Response(
            content=str(response),
            media_type="application/xml"
        )

    prompt = f"""
{SYSTEM_PROMPT}

User said: {SpeechResult}
"""

    try:
        print("Sending request to Gemini...")

        result = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        print("Gemini returned:")
        print(result)

        ai_text = ""

        if hasattr(result, "text"):
            ai_text = (result.text or "").strip()

        if not ai_text:
            ai_text = "Could you repeat that?"

    except Exception as e:

        print("================================")
        print("GEMINI ERROR")
        print("Type:", type(e).__name__)
        print("Message:", str(e))
        traceback.print_exc()
        print("================================")

        ai_text = f"Error: {type(e).__name__}"

    print("AI Response:", ai_text)

    response.say(ai_text, voice="alice")
    response.append(Pause(length=1))

    gather = Gather(
        input="speech",
        action="https://asdasdasdasdasdasda-1.onrender.com/process",
        method="POST",
        speech_timeout="2"
    )

    response.append(gather)

    return Response(
        content=str(response),
        media_type="application/xml"
    )
