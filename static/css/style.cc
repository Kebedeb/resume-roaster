/* ══════════════════════════════
   RESET & VARIABLES
══════════════════════════════ */
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

:root {
  --bg:        #080808;
  --surface:   #111111;
  --surface2:  #1a1a1a;
  --border:    #252525;
  --accent:    #ff4500;
  --accent2:   #ff6b35;
  --text:      #f0f0f0;
  --muted:     #777;
  --green:     #22c55e;
  --yellow:    #f59e0b;
  --red:       #ef4444;
  --radius:    14px;
}

body {
  background: var(--bg);
  color: var(--text);
  font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
  min-height: 100vh;
  line-height: 1.6;
}

/* ══════════════════════════════
   SCREENS
══════════════════════════════ */
.screen {
  display: none;
  min-height: 100vh;
}

.screen.active {
  display: flex;
  align-items: center;
  justify-content: center;
}

#screen-setup.active,
#screen-results.active {
  align-items: flex-start;
  padding: 48px 20px 80px;
}

/* ══════════════════════════════
   LANDING
══════════════════════════════ */
.hero {
  text-align: center;
  max-width: 560px;
  padding: 40px 24px;
}

.hero-fire {
  font-size: 5rem;
  margin-bottom: 16px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50%       { transform: translateY(-12px); }
}

.hero h1 {
  font-size: clamp(2.8rem, 9vw, 5.5rem);
  font-weight: 900;
  letter-spacing: -0.02em;
  background: linear-gradient(135deg, var(--accent), var(--accent2), #ffaa00);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 20px;
}

.tagline {
  font-size: 1.2rem;
  color: var(--text);
  margin-bottom: 8px;
}

.sub {
  font-size: 1rem;
  color: var(--muted);
  margin-bottom: 40px;
}

/* ══════════════════════════════
   CONTAINER
══════════════════════════════ */
.container {
  width: 100%;
  max-width: 780px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-title {
  font-size: 1.6rem;
  font-weight: 800;
}

/* ══════════════════════════════
   CARDS
══════════════════════════════ */
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 24px;
}

.card h3 {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--accent);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 6px;
}

.card-sub {
  font-size: 0.85rem;
  color: var(--muted);
  margin-bottom: 16px;
}

/* ══════════════════════════════
   BUTTONS
══════════════════════════════ */
.btn-primary {
  display: block;
  width: 100%;
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  color: #fff;
  border: none;
  padding: 18px 40px;
  border-radius: 50px;
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
  margin-top: 4px;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(255, 69, 0, 0.35);
}

.btn-primary:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.btn-secondary {
  background: var(--surface2);
  color: var(--text);
  border: 1px solid var(--border);
  padding: 10px 18px;
  border-radius: 8px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-secondary:hover {
  border-color: var(--accent);
  color: var(--accent);
}

/* ══════════════════════════════
   CELEBRITY GRID
══════════════════════════════ */
.celebrity-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
  gap: 12px;
}

.celebrity-card {
  background: var(--surface2);
  border: 2px solid var(--border);
  border-radius: var(--radius);
  padding: 18px 14px;
  cursor: pointer;
  transition: all 0.18s;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.celebrity-card::after {
  content: '🔊 Tap to preview';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(255,69,0,0.9);
  color: white;
  font-size: 0.72rem;
  font-weight: 600;
  padding: 5px;
  transform: translateY(100%);
  transition: transform 0.18s;
}

.celebrity-card:hover::after {
  transform: translateY(0);
}

.celebrity-card:hover {
  border-color: var(--accent);
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(255,69,0,0.2);
}

.celebrity-card.selected {
  border-color: var(--accent);
  background: rgba(255,69,0,0.08);
}

.celebrity-card .c-emoji {
  font-size: 2.8rem;
  display: block;
  margin-bottom: 10px;
}

.celebrity-card .c-name {
  font-weight: 700;
  font-size: 0.95rem;
}

.celebrity-card .c-desc {
  color: var(--muted);
  font-size: 0.78rem;
  margin-top: 4px;
}

.celebrity-card.previewing {
  border-color: var(--accent2);
  animation: pulse-border 1s ease-in-out infinite;
}

@keyframes pulse-border {
  0%, 100% { box-shadow: 0 0 0 0 rgba(255,69,0,0.4); }
  50%       { box-shadow: 0 0 0 6px rgba(255,69,0,0); }
}

/* ══════════════════════════════
   INTENSITY SLIDER
══════════════════════════════ */
.slider-wrap {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 12px;
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  color: var(--muted);
}

input[type="range"] {
  width: 100%;
  height: 6px;
  accent-color: var(--accent);
  cursor: pointer;
}

.intensity-display {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

#intensity-value {
  font-size: 2.4rem;
  font-weight: 900;
  color: var(--accent);
  line-height: 1;
}

#intensity-label {
  color: var(--muted);
  font-size: 0.95rem;
}

/* ══════════════════════════════
   DROPZONE
══════════════════════════════ */
.dropzone {
  border: 2px dashed var(--border);
  border-radius: var(--radius);
  padding: 52px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.18s;
  margin-top: 8px;
}

.dropzone:hover,
.dropzone.dragover {
  border-color: var(--accent);
  background: rgba(255,69,0,0.04);
}

.upload-icon {
  font-size: 3rem;
  display: block;
  margin-bottom: 12px;
}

.dropzone p         { color: var(--muted); font-size: 0.95rem; }
.dropzone p.small   { font-size: 0.8rem; margin-top: 5px; }

.file-status {
  margin-top: 12px;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 0.9rem;
}

.file-status.success {
  background: rgba(34,197,94,0.08);
  color: var(--green);
  border: 1px solid rgba(34,197,94,0.3);
}

.file-status.error {
  background: rgba(239,68,68,0.08);
  color: var(--red);
  border: 1px solid rgba(239,68,68,0.3);
}

.hidden { display: none !important; }

/* ══════════════════════════════
   LOADING
══════════════════════════════ */
.loading-wrap {
  text-align: center;
  padding: 48px 24px;
}

.fire-pulse {
  font-size: 5rem;
  display: block;
  margin-bottom: 24px;
  animation: fire-bounce 0.8s ease-in-out infinite;
}

@keyframes fire-bounce {
  0%, 100% { transform: scale(1) rotate(-3deg); }
  50%       { transform: scale(1.2) rotate(3deg); }
}

#loading-message {
  font-size: 1.3rem;
  font-weight: 700;
  margin-bottom: 8px;
}

.loading-celebrity {
  color: var(--muted);
  font-size: 0.95rem;
  margin-bottom: 32px;
}

.progress-bar {
  width: 280px;
  height: 5px;
  background: var(--surface2);
  border-radius: 99px;
  margin: 0 auto;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent), var(--accent2));
  border-radius: 99px;
  animation: progress-anim 2.5s ease-in-out infinite;
}

@keyframes progress-anim {
  0%   { width: 5%; }
  50%  { width: 75%; }
  100% { width: 95%; }
}

/* ══════════════════════════════
   RESULTS
══════════════════════════════ */
.results-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 4px;
}

.results-header h2 { font-size: 1.6rem; font-weight: 800; }
.results-sub { color: var(--muted); font-size: 0.9rem; margin-top: 2px; }
.results-actions { display: flex; gap: 8px; flex-wrap: wrap; }

/* Audio card */
.audio-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  background: linear-gradient(135deg, rgba(255,69,0,0.08), rgba(255,107,53,0.04));
  border-color: rgba(255,69,0,0.25);
}

.audio-info { display: flex; align-items: center; gap: 14px; }
.audio-emoji { font-size: 2.2rem; }
.audio-title { font-weight: 700; font-size: 1rem; }
.audio-sub { color: var(--muted); font-size: 0.82rem; }

.btn-play {
  background: var(--accent);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 50px;
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
  min-width: 110px;
}

.btn-play:hover  { background: var(--accent2); transform: scale(1.03); }
.btn-play:disabled { opacity: 0.5; cursor: not-allowed; }

/* Scores */
.scores-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 10px;
  margin-top: 8px;
}

.score-item {
  background: var(--surface2);
  border-radius: 10px;
  padding: 14px 10px;
  text-align: center;
}

.score-num  { font-size: 2rem; font-weight: 900; line-height: 1; }
.score-lbl  { font-size: 0.72rem; color: var(--muted); margin-top: 5px; }

/* Roast content */
.roast-content {
  font-size: 0.97rem;
  line-height: 1.85;
  white-space: pre-wrap;
  word-break: break-word;
}