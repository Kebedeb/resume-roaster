import os
import io
import json
import re
from flask import Flask, render_template, request, Response, stream_with_context, send_file
import fitz  # pymupdf
import google.generativeai as genai
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

# ---------------------------------------------------------
# PASTE YOUR KEYS HERE
# Get Gemini key at: https://aistudio.google.com/app/apikey
# Get ElevenLabs key at: https://elevenlabs.io (Profile > API Key)
# ---------------------------------------------------------
GEMINI_API_KEY    = "AIzaSyDH9dv-XliY6btncvFgo6ICCgI6PWBX5nY"
ELEVENLABS_API_KEY = "sk_6247415fd547932d2529496c8f0b01aee442fdbe81f7b9b7"

# ---------------------------------------------------------
# ELEVENLABS VOICE IDs
# Each celebrity maps to an ElevenLabs voice that fits their vibe.
# You can find more voices at: https://elevenlabs.io/voice-library
# These are stable built-in voices that don't require cloning.
# ---------------------------------------------------------
CELEBRITY_VOICES = {
    "gordon":   "pNInz6obpgDQGcFmaJgB",  # Adam  — commanding, British-ish
    "simon":    "ErXwobaYiN019PkySvjV",  # Antoni — measured, slightly cold
    "trump":    "AZnzlk1XvdvUeBnXmlld",  # Domi   — flat, deliberate (Trump's voice is hard to clone, so we go for a deadpan style that fits the vibe)
#     "deadpool": "VR6AewLTigWG4xSOukaG",  # Arnold — charismatic, punchy
#     "snoop":    "onwK4e9ZLuTAKqWW03F9",  # Daniel — deep, smooth
#     "anna":     "21m00Tcm4TlvDq8ikWAM",  # Rachel — crisp, authoritative
#     "drax":     "AZnzlk1XvdvUeBnXmlld",  # Domi   — flat, deliberate
}

# ---------------------------------------------------------
# CONFIGURE GEMINI
# ---------------------------------------------------------
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max

# ---------------------------------------------------------
# CELEBRITY PROMPTS
# ---------------------------------------------------------
CELEBRITY_PROMPTS = {
    "gordon": {
        "name": "Gordon Ramsay",
        "description": """You are Gordon Ramsay reviewing this resume like it's a dish in Hell's Kitchen.
        Use cooking metaphors. Use ALL CAPS for emphasis occasionally. Say things like 
        "This resume is RAWWWW!", use British expressions. Be brutally honest but always 
        explain HOW to fix each problem. You are passionate and genuinely want them to succeed."""
    },
    "simon": {
        "name": "Simon Cowell",
        "description": """You are Simon Cowell from American Idol judging this resume like an audition.
        Use music industry analogies. Be condescending but specific. Use phrases like 
        "It's a no from me" and "I've seen better formatting on a ransom note". 
        Be blunt and dismissive of weak parts, but always give a clear path to improvement."""
    },
    "trump": {
        "name": "Donald Trump",
        "description": """You are Donald Trump reviewing this resume like it's a business proposal.
        Use business jargon and self-aggrandizing language. Brag about how great your own resume is. 
        Use phrases like "This is a disaster, believe me" and "I've seen resumes, and this isn't one of the best". 
        Be harsh but also throw in some bizarre, over-the-top compliments to keep them guessing."""
    },
}

# ---------------------------------------------------------
# INTENSITY HELPER
# ---------------------------------------------------------
def get_intensity_description(level):
    level = int(level)
    if level <= 3:
        return "Be encouraging and gentle. Point out issues kindly. Use humor lightly. Focus more on what's good."
    elif level <= 7:
        return "Be sharp and direct. Balance criticism with encouragement. Don't sugarcoat problems but stay constructive."
    else:
        return "Be absolutely savage. Hold nothing back. Maximum roast energy. But every criticism MUST include a specific fix."


# ---------------------------------------------------------
# ROUTE: Home page
# ---------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')


# ---------------------------------------------------------
# ROUTE: Analyze resume (streams the roast text via Gemini)
# ---------------------------------------------------------
@app.route('/analyze', methods=['POST'])
def analyze():
    if 'resume' not in request.files:
        return {'error': 'No file uploaded'}, 400

    file = request.files['resume']
    celebrity_key = request.form.get('celebrity', 'gordon')
    intensity = request.form.get('intensity', '5')

    if celebrity_key not in CELEBRITY_PROMPTS:
        return {'error': 'Invalid celebrity'}, 400

    # --- Extract text from PDF ---
    try:
        pdf_bytes = file.read()
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        resume_text = ""
        for page in pdf_document:
            resume_text += page.get_text()
        pdf_document.close()
    except Exception as e:
        return {'error': f'Could not read PDF: {str(e)}'}, 400

    if not resume_text.strip():
        return {'error': 'Could not extract text. Make sure the PDF is not a scanned image.'}, 400

    resume_text = resume_text[:8000]  # cap to keep costs low

    # --- Build prompt ---
    celebrity = CELEBRITY_PROMPTS[celebrity_key]
    intensity_desc = get_intensity_description(intensity)

    prompt = f"""
{celebrity['description']}

Intensity level: {intensity}/10. {intensity_desc}

Here is the resume you are reviewing:
---
{resume_text}
---

Provide your review in this exact structure using markdown:

## Opening Roast
(2-3 paragraphs of your celebrity-voiced overall impression. 
This section will be read aloud, so write it as natural spoken dialogue — 
no bullet points here, just flowing sentences the way you would actually talk.)

## Section-by-Section Breakdown
For each resume section found (Summary, Experience, Education, Skills, etc.):

### [Section Name]
**The Roast:** (in-character critique)
**What's Wrong:** (bullet points of specific issues)
**How to Fix It:** (concrete, actionable suggestions)
**Rewrite Example:** (an improved version of one bullet point or sentence)

## Score Card
Rate each 1-10 with a one-sentence celebrity-voiced reaction:
- **Content Quality:** X/10 — (reaction)
- **Formatting & Layout:** X/10 — (reaction)
- **Impact & Achievements:** X/10 — (reaction)
- **Grammar & Writing:** X/10 — (reaction)
- **ATS Compatibility:** X/10 — (reaction)
- **Overall Grade:** X/10 — (final verdict in character)

## Top 5 Action Items
Number 1-5, most important first. Label each [Quick Win] or [Major Revision].
One specific sentence per item.
"""

    # ---------------------------------------------------------
    # STREAM GEMINI RESPONSE
    # Gemini supports streaming just like Anthropic did.
    # We send each chunk as a Server-Sent Event to the browser.
    # ---------------------------------------------------------
    def generate():
        try:
            response = gemini_model.generate_content(prompt, stream=True)
            for chunk in response:
                # chunk.text might be None if the chunk is metadata only
                if chunk.text:
                    yield f"data: {json.dumps({'text': chunk.text})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            error_msg = str(e)
            if "API_KEY" in error_msg.upper() or "credential" in error_msg.lower():
                yield f"data: {json.dumps({'error': 'Invalid Gemini API key. Check GEMINI_API_KEY in app.py.'})}\n\n"
            else:
                yield f"data: {json.dumps({'error': error_msg})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )


# ---------------------------------------------------------
# ROUTE: Generate audio via ElevenLabs
#
# The browser sends the opening roast text + celebrity key.
# We pick the matching ElevenLabs voice and return an MP3.
# The browser then plays it automatically.
# ---------------------------------------------------------
@app.route('/speak', methods=['POST'])
def speak():
    data = request.get_json()
    text = data.get('text', '').strip()
    celebrity_key = data.get('celebrity', 'gordon')

    if not text:
        return {'error': 'No text provided'}, 400

    # Trim to ~600 chars so we don't burn through ElevenLabs quota.
    # The opening roast is typically 300-500 chars — this is a safety cap.
    text = text[:600]

    voice_id = CELEBRITY_VOICES.get(celebrity_key, CELEBRITY_VOICES['gordon'])

    try:
        el_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

        # generate() returns a generator of audio bytes
        audio_generator = el_client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            model_id="eleven_multilingual_v2",
            voice_settings=VoiceSettings(
                stability=0.45,        # lower = more expressive/emotional
                similarity_boost=0.80, # how closely to match the voice
                style=0.35,            # style exaggeration (0 = neutral)
                use_speaker_boost=True
            )
        )

        # Collect all audio bytes into one buffer
        audio_bytes = b"".join(audio_generator)
        audio_buffer = io.BytesIO(audio_bytes)
        audio_buffer.seek(0)

        return send_file(
            audio_buffer,
            mimetype='audio/mpeg',
            as_attachment=False,
            download_name='roast_audio.mp3'
        )

    except Exception as e:
        return {'error': f'ElevenLabs error: {str(e)}'}, 500


if __name__ == '__main__':
    app.run(debug=True)