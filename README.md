🔥 Resume Roaster

**Breaking the awkward silence between your resume and the trash bin — with celebrity voices.**


🚀 Inspiration

We have all sent out dozens of resumes and heard nothing back. The feedback loop in job hunting is broken, applicants get no signal, no explanation, and no idea what went wrong. We wanted to fix that, but in a way that was actually fun to engage with. What if the most brutally honest resume feedback you ever got was delivered by Gordon Ramsay? What if Simon Cowell told you your bullet points were the worst thing he had ever read? We built Resume Roaster to make resume improvement entertaining, immediate, constructive and actionable.


💡 What It Does

Resume Roaster is a full-stack web application that takes your uploaded resume and tears it apart constructively in the voice of a celebrity of your choosing.

- Upload your resume as a PDF via drag-and-drop
- Choose your roaster — Gordon Ramsay, Simon Cowell, or Donald Trump
- Set the intensity from 1 (gentle nudge) to 10 (full devastation)
- Receive a structured roast including scores across four categories (ATS, Grammar, Impact, Style), a punchy opening roast, a prioritized fix-it list, and a closing verdict
- Hear it spoken aloud — the opening roast is automatically converted to audio and played back in a voice styled to match the celebrity
- Copy or export the full feedback for later use

All processing happens in real time with streamed responses so you see the roast being written live.

---

🛠️ How We Built It

Backend — Python / Flask
- `Flask` serves all routes and handles file uploads
- `PyMuPDF (fitz)` extracts text from uploaded PDF resumes on the server
- `Google Gemini 2.5 Flash` generates the structured roast via streaming, so the response appears word by word in real time
- `ElevenLabs Multilingual v2` converts the opening roast text to speech using voice configurations tuned per celebrity
- Server-Sent Events (SSE) stream the Gemini response to the frontend without blocking

Frontend — HTML / CSS / Vanilla JavaScript
- Single page application with four states: setup, loading, results
- Custom markdown-to-HTML parser renders the structured roast output cleanly
- Web Audio API plays the ElevenLabs generated audio automatically on results load
- Fully responsive dark mode design with animated score cards

**AI Models Used**

 Gemini 2.5 Flash Lite | Resume analysis, structured roast generation, scoring |
 ElevenLabs Multilingual v2 | Celebrity-styled voice synthesis for audio playback |

---

⚡ Challenges We Ran Into


- **Markdown rendering** — the fix-it list was rendering as a paragraph instead of a structured list because bold markers were being processed before bullet markers; reordering the replacements fixed it.
- **Keeping it funny AND useful** — prompting a model to be savage while still giving actionable feedback required several iterations of system prompt tuning.

---

🏅 Accomplishments We Are Proud Of

- ✅ Real-time streaming roast that appears word by word like a live performance
- ✅ Voice audio that sounds close enough to the chosen celebrity
- ✅ Clean structured output — scores, fix-it list, and verdict — parsed from a single streamed response
- ✅ A funny product that people may actually want to use on their own resume
- ✅ Full stack built and working end to end within the hackathon window
- ✅ Actually building something.

---

📚 What We Learned

- How to use Server-Sent Events in Flask to stream AI responses to a browser in real time
- How to engineer prompts that produce both structured data (scores) and creative content (roast) in a single generation
- How to work with the ElevenLabs SDK for voice synthesis and tune voice settings to shape personality
- How to parse and render streaming markdown progressively without waiting for the full response
- How to scope a 24-hour project so that every feature that ships actually works

---

🚀 What Is Next for Resume Roaster

- Add more celebrity roasters — we want Snoop Dogg, Anna Wintour, and Drax from Guardians of the Galaxy
- Industry-specific analysis — a tech resume roast should feel different from a finance resume roast
- Before and after view — apply the fix-it suggestions and see a rewritten version side by side
- Cover letter roaster — extend the same experience to cover letters
- Live roasting — display the pdf and highlight on the parts receiving "critique" 

🧰 Built With

- `python`
- `flask`
- `google-gemini`
- `elevenlabs`
- `pymupdf`
- `javascript`
- `html`
- `css`
- `server-sent-events`

---

## 📁 Project Structure

```
resume-roaster/
├── app.py              ← Flask server, all API routes, Gemini + ElevenLabs logic
├── requirements.txt    ← Python dependencies
├── .env                ← API keys (not committed)
├── .gitignore
├── templates/
│   └── index.html      ← Full frontend — all screens, JS logic, markdown renderer
└── static/
    └── style.css       ← Dark mode design, score cards, celebrity grid
```

---

## ⚙️ How to Run It Locally

**1. Clone the repo**
```bash
git clone https://github.com/YOUR_USERNAME/resume-roaster.git
cd resume-roaster
```

**2. Create a virtual environment and install dependencies**
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
pip install -r requirements.txt
```

**3. Add your API keys**

Create a `.env` file in the root:
```
GEMINI_API_KEY=your-gemini-key-here
ELEVENLABS_API_KEY=your-elevenlabs-key-here
```

Get your Gemini key at [aistudio.google.com](https://aistudio.google.com)
Get your ElevenLabs key at [elevenlabs.io](https://elevenlabs.io)

**4. Run the app**
```bash
python app.py
```

**5. Open in your browser**
```
http://localhost:8000
```

---

👥 Created By

Rayyan Madraswala - Chief logistics officer of career despair
Biruk Kebede - Chief emotional damage architect  
