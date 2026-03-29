import os
import io
import json
from flask import Flask, render_template, request, Response, stream_with_context, send_file
import fitz  # pymupdf
# FIX 1: Updated the import to use the new Google GenAI SDK
from google import genai 
from google.genai import types
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

# --- CONFIG ---
# Bhai, keep these keys in an .env file for the final demo!
GEMINI_API_KEY = "AIzaSyBd6Vyh0p4Lni443d9JX88GvUopMzMj2GQ"
ELEVENLABS_API_KEY = "sk_6247415fd547932d2529496c8f0b01aee442fdbe81f7b9b7"

# Stable Voice IDs
CELEBRITY_VOICES = { 
    "gordon": "onwK4e9ZLuTAKqWW03F9", # Daniel (Commanding)
    "simon":  "ErXwobaYiN019PkySvjV", # Antoni (Cold)
    "trump":  "pNInz6obpgDQGcFmaJgB", # Adam (Authoritative)
}

# FIX 2: Initialize the NEW Client instead of using genai.configure
client = genai.Client(api_key=GEMINI_API_KEY)
# We define the model as a string now
MODEL_NAME = "gemini-2.5-flash-lite" 

app = Flask(__name__)

CELEBRITY_PROMPTS = {
    "gordon": {
        "name": "Gordon Ramsay",
        "description": "You are Gordon Ramsay. Use cooking metaphors. Brutally honest, high energy, British slang. 'This resume is RAWWWW!'"
    },
    "simon": {
        "name": "Simon Cowell",
        "description": "You are Simon Cowell. Music industry analogies. Blunt, dismissive, 'It's a no from me'."
    },
    "trump": {
        "name": "Donald Trump",
        "description": "You are Donald Trump. Business jargon, self-aggrandizing, 'This is a disaster, believe me'."
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    file = request.files.get('resume')
    celebrity_key = request.form.get('celebrity', 'gordon')
    intensity = request.form.get('intensity', '5')

    if not file: return {'error': 'No file'}, 400

    pdf_bytes = file.read()
    pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
    resume_text = "".join([page.get_text() for page in pdf_document])[:6000]
    pdf_document.close()

    celebrity = CELEBRITY_PROMPTS.get(celebrity_key, CELEBRITY_PROMPTS['gordon'])
    
    prompt = f"""
    {celebrity['description']}
    Intensity: {intensity}/10.
    Resume: {resume_text}

    Format your response EXACTLY like this:
    [SCORES]
    ATS: X/10
    Grammar: X/10
    Impact: X/10
    Style: X/10
    Overall: X/10
    [/SCORES]

    ## Opening Roast
    (2 paragraphs of spoken dialogue for the audio)

    ## The Fix-It List
    (3-5 concise bullet points of major issues)
    """
    def generate():
        try:
            print(f"--- Starting Gemini Stream for {celebrity_key} ---")
            
            # Use the most stable streaming syntax for the new SDK
            response = client.models.generate_content_stream(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7  # You can put other settings here, but NOT 'stream'
                )
            )

            for chunk in response:
                if chunk.text:
                    # Print to terminal so you know it's working!
                    print(f"Chunk received: {chunk.text[:20]}...") 
                    yield f"data: {json.dumps({'text': chunk.text})}\n\n"

            print("--- Stream Complete ---")
            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            print(f"!!! BACKEND ERROR: {str(e)}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    # def generate():
    #     try:
    #         # FIX 3: Updated streaming syntax for the new google-genai SDK
    #         response = client.models.generate_content(
    #             model=MODEL_NAME,
    #             contents=prompt,
    #             config={'stream': True}
    #         )
    #         for chunk in response:
    #             if chunk.text: 
    #                 yield f"data: {json.dumps({'text': chunk.text})}\n\n"
    #         yield f"data: {json.dumps({'done': True})}\n\n"
    #     except Exception as e:
    #         yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@app.route('/speak', methods=['POST'])
def speak():
    data = request.get_json()
    text = data.get('text', '').strip()
    celebrity_key = data.get('celebrity', 'gordon')

    if not text:
        return {'error': 'No text provided'}, 400

    # Ensure these IDs are the stable ones
    voice_id = CELEBRITY_VOICES.get(celebrity_key, "onwK4e9ZLuTAKqWW03F9") 

    try:
        print(f"--- Voice Request for {celebrity_key} ---")
        el_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

        # FIX: The new SDK uses .text_to_speech.convert
        audio_generator = el_client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            model_id="eleven_multilingual_v2",
            voice_settings=VoiceSettings(
                stability=0.5,
                similarity_boost=0.8,
                style=0.0,
                use_speaker_boost=True
            )
        )
        
        # Combine the generator chunks into one byte string
        audio_bytes = b"".join(audio_generator)
        
        return send_file(
            io.BytesIO(audio_bytes),
            mimetype='audio/mpeg',
            as_attachment=False
        )

    except Exception as e:
        print(f"!!! ELEVENLABS ERROR: {str(e)}")
        return {'error': str(e)}, 500
# @app.route('/speak', methods=['POST'])
# def speak():
#     data = request.get_json()
#     voice_id = CELEBRITY_VOICES.get(data.get('celebrity'), CELEBRITY_VOICES['gordon'])
#     el_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    
#     # ... your existing ElevenLabs logic ...
#     return {'status': 'Audio logic placeholder'}

if __name__ == '__main__':
    # Running on port 8000 as you requested
    app.run(debug=True, port=8000)