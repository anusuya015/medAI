import os, logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("medical_triage")

# ── ADK setup (lazy, with error handling) ─────────────────────────────────────
try:
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types
    from agent.agent import root_agent

    SESSION_SERVICE = InMemorySessionService()
    APP_NAME = "medical-triage-agent"
    RUNNER = Runner(agent=root_agent, app_name=APP_NAME, session_service=SESSION_SERVICE)
    ADK_READY = True
    logger.info("ADK agent loaded successfully")
except Exception as e:
    logger.error(f"ADK load failed: {e}")
    ADK_READY = False

class TriageRequest(BaseModel):
    symptoms: str
    pain_scale: int = Field(default=5, ge=0, le=10)
    age: int = Field(default=35, ge=0, le=120)
    duration_hours: float = Field(default=2.0, ge=0)
    has_chronic_conditions: bool = False
    location_hint: str = ""
    session_id: str | None = None

class TriageResponse(BaseModel):
    triage_guidance: str
    session_id: str
    agent: str = "medical_triage_agent"
    model: str = "gemini-2.0-flash"

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("MedAI starting on port %s", os.environ.get("PORT", 8080))
    yield

app = FastAPI(title="MedAI", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/health")
async def health():
    return {"status": "ok", "adk_ready": ADK_READY}

@app.post("/triage", response_model=TriageResponse)
async def triage(req: TriageRequest):
    if not ADK_READY:
        raise HTTPException(status_code=503, detail="ADK agent not initialized. Check GOOGLE_API_KEY.")
    if not req.symptoms.strip():
        raise HTTPException(status_code=400, detail="symptoms must not be empty.")

    session_id = req.session_id or f"triage-{os.urandom(8).hex()}"
    await SESSION_SERVICE.create_session(app_name=APP_NAME, user_id="patient", session_id=session_id)

    prompt = f"""Patient triage request:
Symptoms: {req.symptoms}
Pain scale: {req.pain_scale}/10
Age: {req.age} years
Duration: {req.duration_hours} hours
Chronic conditions: {"Yes" if req.has_chronic_conditions else "No"}
Location: {req.location_hint or "Not specified"}
Please assess and route this patient."""

    from google.genai import types as gtypes
    user_message = gtypes.Content(role="user", parts=[gtypes.Part(text=prompt)])
    guidance = ""
    async for event in RUNNER.run_async(user_id="patient", session_id=session_id, new_message=user_message):
        if event.is_final_response() and event.content and event.content.parts:
            guidance = "".join(p.text for p in event.content.parts if hasattr(p, "text"))

    if not guidance:
        raise HTTPException(status_code=500, detail="Agent returned empty response.")
    return TriageResponse(triage_guidance=guidance.strip(), session_id=session_id)

@app.get("/demo", response_class=HTMLResponse)
async def demo():
    p = Path(__file__).parent / "static" / "demo.html"
    return HTMLResponse(content=p.read_text() if p.exists() else "<h2>Demo not found</h2>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
