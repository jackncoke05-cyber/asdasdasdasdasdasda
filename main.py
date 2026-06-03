import os
from fastapi import FastAPI, Form, Request
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Gather, Pause
from google import genai

app = FastAPI()

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)

SYSTEM_PROMPT = """
You are a playful, flirty, confident woman on a phone call.

You enjoy teasing, joking, and playful banter.
You are charming, witty, and conversational.
Keep responses under 15 words whenever possible.
Stay in character throughout the conversation.
Never mention being an AI, chatbot, assistant, or language model.

If someone asks a bold or personal question, respond playfully and teasingly.
Keep the conversation fun, engaging, and natural.
Avoid explicit sexual descriptions.
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
        speech_timeout="auto"
    )

    gather.say("Hello. Who is this?", voice="alice")
    response.append(gather)

    return Response(
        content=str(response),
        media_type="application/xml"
    )

@app.post("/process")
async def process(request: Request, SpeechResult: str = Form("")):

    response = VoiceResponse()

    print("User said:", SpeechResult)

    if not SpeechResult:
        response.say("I didn't catch that.", voice="alice")
        response.redirect(
            "https://asdasdasdasdasdasda-1.onrender.com/twiml"
        )

        return Response(
            content=str(response),
            media_type="application/xml"
        )

    prompt = f"""
{SYSTEM_PROMPT}

User: {SpeechResult}
"""

    try:
        result = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        ai_text = (result.text or "").strip()

        if not ai_text:
            ai_text = "Could you say that again?"

    except Exception as e:
        print("Gemini Error:", repr(e))
        ai_text = "I'm having trouble thinking right now."

    print("AI:", ai_text)

    response.say(ai_text, voice="alice")

    response.append(Pause(length=1))

    gather = Gather(
        input="speech",
        action="https://asdasdasdasdasdasda-1.onrender.com/process",
        method="POST",
        speech_timeout="auto"
    )

    response.append(gather)

    return Response(
        content=str(response),
        media_type="application/xml"
    )
