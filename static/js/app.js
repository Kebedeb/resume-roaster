// ════════════════════════════════════════
// STATE
// ════════════════════════════════════════
const state = {
  celebrity: null,
  intensity: 5,
  resumeText: "",
  openingRoastText: "",
  currentAudio: null,
  audioBlob: null
};

// ════════════════════════════════════════
// INIT
// ════════════════════════════════════════
document.addEventListener("DOMContentLoaded", () => {
  renderCelebrities();
});

// ════════════════════════════════════════
// SCREEN NAVIGATION
// ════════════════════════════════════════
function showScreen(id) {
  document.querySelectorAll(".screen").forEach(s => s.classList.remove("active"));
  document.getElementById(id).classList.add("active");
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function resetApp() {
  state.celebrity = null;
  state.resumeText = "";
  state.openingRoastText = "";
  state.audioBlob = null;
  stopAudio();

  document.querySelectorAll(".celebrity-card").forEach(c => c.classList.remove("selected"));
  document.getElementById("file-status").className = "file-status hidden";
  document.getElementById("file-status").textContent = "";
  document.getElementById("roast-content").textContent = "";
  document.getElementById("scores-grid").innerHTML = "";
  document.getElementById("roast-btn").disabled = true;

  showScreen("screen-setup");
}

// ════════════════════════════════════════
// RENDER CELEBRITIES
// ════════════════════════════════════════
function renderCelebrities() {
  const grid = document.getElementById("celebrity-grid");
  grid.innerHTML = CELEBRITIES.map(c => `
    <div
      class="celebrity-card"
      id="celeb-${c.id}"
      onclick="selectCelebrity('${c.id}')"
    >
      <span class="c-emoji">${c.emoji}</span>
      <div class="c-name">${c.name}</div>
      <div class="c-desc">${c.desc}</div>
    </div>
  `).join("");
}

// ════════════════════════════════════════
// SELECT CELEBRITY + PLAY PREVIEW
// ════════════════════════════════════════
async function selectCelebrity(id) {
  // Update selection UI
  document.querySelectorAll(".celebrity-card").forEach(c => {
    c.classList.remove("selected", "previewing");
  });
  const card = document.getElementById(`celeb-${id}`);
  card.classList.add("selected", "previewing");

  // Update state
  state.celebrity = CELEBRITIES.find(c => c.id === id);
  checkReady();

  // Stop any playing audio
  stopAudio();

  // Fetch and play voice preview
  try {
    const res = await fetch("/voice-preview", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ celebrity_id: id })
    });

    if (res.ok) {
      const blob = await res.blob();
      playAudioBlob(blob);
    }
  } catch (err) {
    console.warn("Voice preview failed:", err);
  } finally {
    card.classList.remove("previewing");
  }
}

// ════════════════════════════════════════
// AUDIO HELPERS
// ════════════════════════════════════════
function playAudioBlob(blob) {
  stopAudio();
  const url = URL.createObjectURL(blob);
  state.currentAudio = new Audio(url);
  state.currentAudio.play().catch(() => {});
}

function stopAudio() {
  if (state.currentAudio) {
    state.currentAudio.pause();
    state.currentAudio.currentTime = 0;
    state.currentAudio = null;
  }
}

// ════════════════════════════════════════
// INTENSITY
// ════════════════════════════════════════
function updateIntensity(value) {
  state.intensity = parseInt(value);
  document.getElementById("intensity-value").textContent = value;

  const labels = {
    1:  "— Barely a tickle",
    2:  "— Mild sting",
    3:  "— Getting warmer",
    4:  "— Sharp but fair",
    5:  "— Sharp but balanced",
    6:  "— Cutting deep",
    7:  "— That actually hurt",
    8:  "— Brutal territory",
    9:  "— No survivors",
    10: "— FULL DEVASTATION 💀"
  };

  document.getElementById("intensity-label").textContent = labels[value] || "";
}

// ════════════════════════════════════════
// FILE HANDLING
// ════════════════════════════════════════
function handleDragOver(e) {
  e.preventDefault();
  document.getElementById("dropzone").classList.add("dragover");
}

function handleDragLeave() {
  document.getElementById("dropzone").classList.remove("dragover");
}

function handleDrop(e) {
  e.preventDefault();
  document.getElementById("dropzone").classList.remove("dragover");
  const file = e.dataTransfer.files[0];
  if (file) processFile(file);
}

function handleFileSelect(e) {
  if (e.target.files[0]) processFile(e.target.files[0]);
}

async function processFile(file) {
  const statusEl = document.getElementById("file-status");
  statusEl.className = "file-status";
  statusEl.textContent = "⏳ Reading your resume...";
  statusEl.classList.remove("hidden");

  const form = new FormData();
  form.append("file", file);

  try {
    const res = await fetch("/parse-pdf", { method: "POST", body: form });
    const data = await res.json();

    if (!res.ok) throw new Error(data.error);

    state.resumeText = data.text;
    statusEl.classList.add("success");
    statusEl.textContent = `✅ ${file.name} — ${data.length.toLocaleString()} characters extracted`;
    checkReady();

  } catch (err) {
    state.resumeText = "";
    statusEl.classList.add("error");
    statusEl.textContent = `❌ ${err.message}`;
    checkReady();
  }
}

// ════════════════════════════════════════
// ENABLE ROAST BUTTON
// ════════════════════════════════════════
function checkReady() {
  const ready = state.celebrity && state.resumeText;
  document.getElementById("roast-btn").disabled = !ready;
}

// ════════════════════════════════════════
// LOADING MESSAGES
// ════════════════════════════════════════
const LOADING_MESSAGES = [
  "Reading your resume with barely concealed horror...",
  "Sharpening the knives...",
  "Preparing feedback you will not enjoy...",
  "Consulting the critics...",
  "Locating every weak bullet point...",
  "Almost ready to ruin your afternoon (helpfully)..."
];

// ════════════════════════════════════════
// START ROAST — MAIN FUNCTION
// ════════════════════════════════════════
async function startRoast() {
  if (!state.celebrity || !state.resumeText) return;

  stopAudio();

  // Switch to loading screen
  showScreen("screen-loading");
  document.getElementById("loading-celebrity").textContent =
    `${state.celebrity.emoji} ${state.celebrity.name} is reviewing your resume...`;

  // Cycle loading messages
  let msgIdx = 0;
  const msgEl = document.getElementById("loading-message");
  msgEl.textContent = LOADING_MESSAGES[0];
  const msgTimer = setInterval(() => {
    msgIdx = (msgIdx + 1) % LOADING_MESSAGES.length;
    msgEl.textContent = LOADING_MESSAGES[msgIdx];
  }, 2800);

  try {
    // Call roast endpoint — get a streaming response
    const res = await fetch("/roast", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        resume_text:      state.resumeText,
        celebrity_style:  state.celebrity.style,
        celebrity_name:   state.celebrity.name,
        intensity:        state.intensity
      })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.error || "Request failed");
    }

    clearInterval(msgTimer);

    // Set up results screen
    document.getElementById("roast-content").textContent = "";
    document.getElementById("scores-grid").innerHTML = "";
    document.getElementById("results-celebrity-name").textContent =
      `Roasted by ${state.celebrity.emoji} ${state.celebrity.name} · Intensity ${state.intensity}/10`;
    document.getElementById("audio-celebrity-emoji").textContent =
      state.celebrity.emoji;
    document.getElementById("play-btn").textContent = "▶ Play";
    document.getElementById("play-btn").disabled = true;

    showScreen("screen-results");

    // Stream the text response
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let fullText = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const lines = decoder.decode(value).split("\n");

      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        const raw = line.slice(6).trim();
        if (raw === "[DONE]") break;

        try {
          const parsed = JSON.parse(raw);
          if (parsed.text) {
            fullText += parsed.text;
            document.getElementById("roast-content").textContent = fullText;
          }
          if (parsed.error) throw new Error(parsed.error);
        } catch {}
      }
    }

    // Render score cards
    renderScores(fullText);

    // Extract opening roast and fetch audio
    extractAndSpeakOpening(fullText);

  } catch (err) {
    clearInterval(msgTimer);
    showScreen("screen-setup");
    alert(`Something went wrong: ${err.message}`);
  }
}

// ════════════════════════════════════════
// EXTRACT OPENING ROAST + FETCH AUDIO
// ════════════════════════════════════════
async function extractAndSpeakOpening(fullText) {
  // Pull out just the opening roast section
  const match = fullText.match(/OPENING ROAST\s*\n([\s\S]*?)(?=##)/i);
  if (!match) return;

  state.openingRoastText = match[1].trim().substring(0, 900);
  if (!state.openingRoastText) return;

  // Fetch audio in background
  try {
    const res = await fetch("/speak-roast", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text:         state.openingRoastText,
        celebrity_id: state.celebrity.id
      })
    });

    if (!res.ok) throw new Error("Audio generation failed");

    state.audioBlob = await res.blob();

    // Enable play button
    const btn = document.getElementById("play-btn");
    btn.disabled = false;
    btn.textContent = "▶ Play";

    // Auto play
    playRoastAudio();

  } catch (err) {
    console.warn("Roast audio failed:", err);
    document.getElementById("play-btn").textContent = "Voice unavailable";
  }
}

// ════════════════════════════════════════
// PLAY BUTTON HANDLER
// ════════════════════════════════════════
function handlePlayButton() {
  if (state.audioBlob) {
    playRoastAudio();
  }
}

function playRoastAudio() {
  if (!state.audioBlob) return;
  stopAudio();

  const btn = document.getElementById("play-btn");
  btn.textContent = "⏸ Playing...";

  playAudioBlob(state.audioBlob);

  state.currentAudio.onended = () => {
    btn.textContent = "▶ Play Again";
  };
}

// ════════════════════════════════════════
// RENDER SCORE CARDS
// ════════════════════════════════════════
function renderScores(text) {
  const categories = [
    "Content Quality",
    "Formatting & Layout",
    "Impact & Achievements",
    "Grammar & Writing",
    "ATS Compatibility",
    "OVERALL"
  ];

  const grid = document.getElementById("scores-grid");
  grid.innerHTML = "";

  categories.forEach(cat => {
    const pattern = new RegExp(`${cat}[:\\s]+(\\d+)/10`, "i");
    const match = text.match(pattern);
    if (!match) return;

    const score = parseInt(match[1]);
    const color = score >= 7
      ? "var(--green)"
      : score >= 4
      ? "var(--yellow)"
      : "var(--red)";

    grid.innerHTML += `
      <div class="score-item">
        <div class="score-num" style="color:${color}">${score}</div>
        <div class="score-lbl">${cat}</div>
      </div>
    `;
  });
}

// ════════════════════════════════════════
// COPY TO CLIPBOARD
// ════════════════════════════════════════
function copyResults() {
  const text = document.getElementById("roast-content").textContent;
  navigator.clipboard.writeText(text)
    .then(() => alert("Copied to clipboard!"))
    .catch(() => alert("Copy failed — try selecting and copying manually"));
}