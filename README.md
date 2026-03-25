# 🤖 MedAI — Medical Triage Agent

An AI-powered medical triage assistant built with Google ADK, FastAPI, and Gemini. It assesses patient symptoms and routes them to the appropriate level of care.

## Features

- 🚨 **4-level triage classification** — Emergency, Urgent Care, Appointment, Self-Care
- 🔴 **Red flag symptom detection** — instantly flags life-threatening symptoms
- 💬 **Conversational AI** — powered by Gemini via Google ADK
- 🌐 **REST API** — FastAPI backend with a clean web UI
- ☁️ **Cloud Run ready** — containerized and deployable in minutes

## Tech Stack

- [Google ADK](https://google.github.io/adk-docs/) — Agent Development Kit
- [Gemini 2.5 Flash](https://ai.google.dev/) — LLM backbone
- [FastAPI](https://fastapi.tiangolo.com/) — API framework
- [Docker](https://www.docker.com/) — containerization
- [Google Cloud Run](https://cloud.google.com/run) — serverless deployment

## Project Structure
```
medical-triage-agent/
├── agent/
│   ├── __init__.py
│   ├── agent.py          # Root agent + tool definitions
│   └── static/
│       └── demo.html     # Web UI
├── main.py               # FastAPI app
├── requirements.txt
└── Dockerfile
```

## Getting Started

### Prerequisites
- Python 3.12+
- Google API Key with Gemini access
- Docker (for containerized deployment)

### Run Locally
```bash
pip install -r requirements.txt
export GOOGLE_API_KEY=your_key_here
uvicorn main:app --host 0.0.0.0 --port 8080
```

Open http://localhost:8080/demo in your browser.

### Deploy to Cloud Run
```bash
export PROJECT_ID=your_gcp_project_id
export GOOGLE_API_KEY=your_key_here

docker build -t gcr.io/$PROJECT_ID/medai-agent . && \
docker push gcr.io/$PROJECT_ID/medai-agent && \
gcloud run deploy medai-agent \
  --image gcr.io/$PROJECT_ID/medai-agent \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi \
  --set-env-vars GOOGLE_API_KEY=$GOOGLE_API_KEY
```

## API Reference

### `GET /health`
Returns agent status.
```json
{ "status": "ok", "adk_ready": true }
```

### `POST /triage`
Assess patient symptoms.

**Request:**
```json
{
  "symptoms": "fever and headache",
  "pain_scale": 6,
  "age": 35,
  "duration_hours": 4,
  "has_chronic_conditions": false,
  "location_hint": "Mumbai"
}
```

**Response:**
```json
{
  "triage_guidance": "⚠️ URGENT CARE ...",
  "session_id": "triage-abc123",
  "agent": "medical_triage_agent",
  "model": "gemini-2.5-flash"
}
```

### `GET /demo`
Opens the web UI.

## Triage Levels

| Level | Criteria | Action |
|-------|----------|--------|
| 🚨 Emergency | Pain ≥9, red flag symptoms | Call 911 / ER immediately |
| ⚠️ Urgent Care | Pain 6–8, rapid worsening, high-risk patient | Within 2–4 hours |
| 📅 Appointment | Pain 3–5, stable, needs evaluation | Within 24–48 hours |
| 🏠 Self-Care | Pain 0–2, minor symptoms | Monitor at home |

## Disclaimer

> This is an AI-assisted triage tool only and is **not a substitute for professional medical advice**. In emergencies, call your local emergency number immediately.

## License

MIT
