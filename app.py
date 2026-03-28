import os
import json
import io
import anthropic
import fitz  # PyMuPDF
from flask import (
    Flask, request, jsonify,
    render_template, Response,
    stream_with_context, send_file
)
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "fallback-secret")


claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
eleven = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))


# VOICE CONFIGURATIONS
# Each celebrity gets tuned voice settings
# that shape personality without cloning


VOICE_CONFIGS = {
    "gordon": {
        "voice_id": "pNInz6obpgDQGcFmaJgB",  # Adam - deep authoritative
        "stability": 0.30,
        "similarity_boost": 0.75,
        "style": 0.85,
        "use_speaker_boost": True,
        "preview": (
            "Right. Hand me that resume. "
            "Bloody hell. This is RAW. Completely RAW. "
            "We are going to go through every single section "
            "and I am going to tell you EXACTLY what went wrong."
        )
    },
    "simon": {
        "voice_id": "pNInz6obpgDQGcFmaJgB",
        "stability": 0.55,
        "similarity_boost": 0.75,
        "style": 0.65,
        "use_speaker_boost": True,
        "preview": (
            "I have seen a lot of resumes in my time. "
            "A lot. And I will be honest with you. "
            "This one is not good. It is really not good. "
            "But let us go through it together."
        )
    },
    "deadpool": {
        "voice_id": "TxGEqnHWrfWFTfGW9XjX",  # Josh - energetic
        "stability": 0.25,
        "similarity_boost": 0.70,
        "style": 0.92,
        "use_speaker_boost": True,
        "preview": (
            "Oh hey! Breaking the fourth wall here. "
            "You actually uploaded your resume to get roasted "
            "by an AI pretending to be me. "
            "That is genuinely the most chaotic thing I have seen today. "
            "And I fought a guy made of sand this morning. Let us do this."
        )
    },
    "snoop": {
        "voice_id": "VR6AewLTigWG4xSOukaG",  # Arnold - deep smooth
        "stability": 0.72,
        "similarity_boost": 0.80,
        "style": 0.60,
        "use_speaker_boost": True,
        "preview": (
            "Aight aight. Snoop D O double G in the building, ya dig? "
            "I got your resume right here. "
            "Now I ain't gonna lie to you. "
            "This thing needs some serious work. "
            "But we gonna get through it together. Fo shizzle."
        )
    },
    "anna": {
        "voice_id": "21m00Tcm4TlvDq8ikWAM",  
        "stability": 0.82,
        "similarity_boost": 0.75,
        "style": 0.45,
        "use_speaker_boost": False,
        "preview": (
            "I see. So this is your resume. "
            "I have looked at it now. "
            "Let us begin."
        )
    },
    "drax": {
        "voice_id": "VR6AewLTigWG4xSOukaG",
        "stability": 0.78,
        "similarity_boost": 0.80,
        "style": 0.35,
        "use_speaker_boost": True,
        "preview": (
            "I have read your resume. All of it. "
            "I do not understand why you have listed "
            "communication skills as a skill. "
            "I am communicating with you right now "
            "and I did not put it on my resume. "
            "This is very confusing to me."
        )
    }
}


# ─────────────────────────────────────────
# HELPER: Generate audio bytes from text
# ─────────────────────────────────────────

def generate_audio(text, celebrity_id):
    config = VOICE_CONFIGS.get(celebrity_id, VOICE_CONFIGS["gordon"])

    audio_stream = eleven.text_to_speech.convert(
        voice_id=config["voice_id"],
        text=text,
        model_id="eleven_turbo_v2_5",
        voice_settings=VoiceSettings(
            stability=config["stability"],
            similarity_boost=config["similarity_boost"],
            style=config["style"],
            use_speaker_boost=config["use_speaker_boost"]
        ),
        output_format="mp3_44100_128"
    )

    audio_bytes = b""
    for chunk in audio_stream:
        audio_bytes += chunk

    return audio_bytes


# ─────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/parse-pdf", methods=["POST"])
def parse_pdf():
    """Receive PDF, extract text using PyMuPDF, return plain text."""

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Please upload a PDF file only"}), 400

    raw = file.read()

    if len(raw) > 5 * 1024 * 1024:
        return jsonify({"error": "File too large. Maximum size is 5MB"}), 400

    try:
        doc = fitz.open(stream=raw, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()

        if not text.strip():
            return jsonify({
                "error": "Could not extract text. Your PDF may be a scanned image."
            }), 400

        return jsonify({
            "text": text.strip(),
            "length": len(text.strip())
        })

    except Exception as e:
        return jsonify({"error": f"PDF parsing failed: {str(e)}"}), 500


@app.route("/voice-preview", methods=["POST"])
def voice_preview():
    """Play a short voice intro when user selects a celebrity."""

    data = request.get_json()
    celebrity_id = data.get("celebrity_id", "gordon")
    config = VOICE_CONFIGS.get(celebrity_id, VOICE_CONFIGS["gordon"])
    preview_text = config["preview"]

    try:
        audio_bytes = generate_audio(preview_text, celebrity_id)
        return send_file(
            io.BytesIO(audio_bytes),
            mimetype="audio/mpeg",
            as_attachment=False
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/roast", methods=["POST"])
def roast():
    """
    Main route. Takes resume text + celebrity choice + intensity.
    Streams Claude's response back as Server-Sent Events.
    """

    data = request.get_json()
    resume_text = data.get("resume_text", "").strip()
    celebrity_style = data.get("celebrity_style", "").strip()
    celebrity_name = data.get("celebrity_name", "").strip()
    intensity = int(data.get("intensity", 5))

    if not resume_text:
        return jsonify({"error": "No resume text provided"}), 400
    if not celebrity_style:
        return jsonify({"error": "No celebrity selected"}), 400

    if intensity <= 3:
        intensity_desc = (
            "Be encouraging with gentle humor. "
            "Constructive but kind. Light roasting only."
        )
    elif intensity <= 7:
        intensity_desc = (
            "Be sharp and cutting. "
            "Balance savage humor with genuinely useful feedback."
        )
    else:
        intensity_desc = (
            "Be completely savage. No mercy whatsoever. "
            "Still provide real actionable advice underneath the brutality."
        )

    prompt = f"""
{celebrity_style}

Intensity level: {intensity}/10. {intensity_desc}

You are reviewing this resume as {celebrity_name}.
Stay completely in character throughout.
Provide your roast in this EXACT structure with these EXACT headers:

## 🔥 OPENING ROAST
[2 to 3 paragraphs of your brutally honest first impression, fully in character]

## 📊 SCORES
Content Quality: X/10
Formatting & Layout: X/10
Impact & Achievements: X/10
Grammar & Writing: X/10
ATS Compatibility: X/10
OVERALL: X/10
[One line celebrity reaction to the overall score]

## 🔍 SECTION BREAKDOWN

### Summary/Objective
**The Roast:** [in character criticism]
**Issues:**
- [specific problem]
- [specific problem]
**Fix It:** [concrete suggestion]
**Rewrite Example:** [show an improved version]

### Experience
**The Roast:** [in character criticism]
**Issues:**
- [specific problem]
- [specific problem]
**Fix It:** [concrete suggestion]
**Rewrite Example:** [improved bullet point]

### Skills
**The Roast:** [in character]
**Issues:**
- [specific problem]
**Fix It:** [concrete suggestion]

### Education & Other Sections
**The Roast:** [in character]
**Issues:**
- [specific problem]
**Fix It:** [concrete suggestion]

## ⚡ TOP 5 ACTION ITEMS
1. [Most critical fix — label as QUICK WIN or MAJOR REVISION]
2. [Second priority]
3. [Third priority]
4. [Fourth priority]
5. [Fifth priority]

## 🎬 CLOSING VERDICT
[One final devastating but oddly encouraging paragraph, fully in character]

Here is the resume:
---
{resume_text}
---
"""

    def generate():
        try:
            with claude.messages.stream(
                model="claude-sonnet-4-6",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            ) as stream:
                for text_chunk in stream.text_stream:
                    yield f"data: {json.dumps({'text': text_chunk})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive"
        }
    )


@app.route("/speak-roast", methods=["POST"])
def speak_roast():
    """
    Takes the opening roast text and converts it to speech
    using the celebrity's voice configuration.
    """

    data = request.get_json()
    text = data.get("text", "").strip()
    celebrity_id = data.get("celebrity_id", "gordon")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    # Trim to keep within ElevenLabs limits and response time reasonable
    text = text[:900]

    try:
        audio_bytes = generate_audio(text, celebrity_id)
        return send_file(
            io.BytesIO(audio_bytes),
            mimetype="audio/mpeg",
            as_attachment=False
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=5000)