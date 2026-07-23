# ResearchPilot AI – Multi-Agent Research Paper Generation System

> Automatically researches a topic using 8 specialized AI agents and generates a downloadable academic PDF.

---

## Architecture

```
User Input
    │
    ▼
Agent 1 – Topic Validator       → validates & enriches topic
    │
Agent 2 – Research Planner      → creates section-by-section plan
    │
Agent 3 – Researcher            → gathers facts, stats, sources per section
    │
Agent 4 – Analyst               → removes noise, structures content
    │
Agent 5 – Academic Writer       → writes full paper (2500+ words)
    │
Agent 6 – Reviewer              → improves grammar, flow, transitions
    │
Agent 7 – Citation Agent        → formats APA 7th edition references
    │
Agent 8 – PDF Builder           → renders professional Times New Roman PDF
    │
    ▼
  PDF Download
```

---

## Folder Structure

```
researchpilot/
├── main.py                  # FastAPI app
├── config.py                # MODEL_NAME + env config
├── requirements.txt
├── .env.example
├── agents/
│   ├── agent1_validator.py
│   ├── agent2_planner.py
│   ├── agent3_researcher.py
│   ├── agent4_analyst.py
│   ├── agent5_writer.py
│   ├── agent6_reviewer.py
│   ├── agent7_citation.py
│   └── agent8_pdf.py
├── services/
│   └── orchestrator.py      # wires all agents together
└── frontend/
    └── index.html           # single-page frontend (no build step)
```

---

## Installation & Setup

### Step 1 – Install Python 3.11+
Download from https://python.org and ensure `python --version` works in your terminal.

### Step 2 – Clone / unzip the project
```bash
cd Desktop
# if using git:
git clone <your-repo-url> researchpilot
cd researchpilot
```

### Step 3 – Create a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### Step 4 – Install dependencies
```bash
pip install -r requirements.txt
```

### Step 5 – Create your .env file
```bash
cp .env.example .env
```
Open `.env` and replace the placeholder with your real OpenAI API key:
```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```
Get your key at: https://platform.openai.com/api-keys

### Step 6 – Run the backend
```bash
uvicorn main:app --reload --port 8000
```
You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 7 – Open the frontend
Just open `frontend/index.html` in your browser (double-click or drag into Chrome).

The frontend is already pointed at `http://127.0.0.1:8000` by default.

---

## Using ngrok (to share publicly / use on mobile)

### Step 1 – Download ngrok
https://ngrok.com/download → sign up free → install

### Step 2 – Expose the backend
```bash
ngrok http 8000
```
You'll get a URL like: `https://abc123.ngrok-free.app`

### Step 3 – Update the frontend
Open `frontend/index.html`, find this line near the top of the `<script>` section:
```js
const API_BASE = "http://127.0.0.1:8000";
```
Replace with your ngrok URL:
```js
const API_BASE = "https://abc123.ngrok-free.app";
```
Save and reload the page.

---

## Deploying Frontend on Netlify

1. Go to https://netlify.com → sign up free.
2. Drag and drop the `frontend/` folder into the Netlify dashboard.
3. Your frontend is live instantly at a `*.netlify.app` URL.
4. Update `API_BASE` in `index.html` to your ngrok or deployed backend URL before deploying.

---

## API Reference

### POST /generate-paper
**Request:**
```json
{ "topic": "Impact of Artificial Intelligence in Healthcare" }
```
**Response:** `application/pdf` (direct file download)

**Headers returned:**
- `X-Word-Count` – approximate word count of the paper
- `X-Reference-Count` – number of APA references generated

### GET /health
Returns `{"status": "ok"}` — use to verify the server is running.

---

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `401 Unauthorized` | Invalid OpenAI key | Check `.env` |
| `422 Unprocessable Entity` | Topic too short | Enter a descriptive topic |
| `500 Internal Server Error` | Agent pipeline failure | Check terminal logs |
| CORS error in browser | Frontend can't reach backend | Ensure backend is running on port 8000 |
| ngrok ERR_NGROK_3004 | Session expired | Restart `ngrok http 8000` |

---

## Changing the Model

Edit `config.py`:
```python
MODEL_NAME = "gpt-4.1-mini"   # change to any OpenAI model here
```
All 8 agents will automatically use the new model.

---

## Future Improvements

- [ ] Add WebSocket streaming for real-time per-agent status updates
- [ ] Add DOCX and Markdown export options
- [ ] Paper history with local SQLite storage
- [ ] Dark/light mode toggle
- [ ] User authentication (JWT)
- [ ] LaTeX export
- [ ] Separate citation download endpoint
