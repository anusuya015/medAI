from google.adk.agents import Agent

def classify_triage_level(symptoms: str, pain_scale: int, duration_hours: float, age: int, has_chronic_conditions: bool) -> dict:
    """Classifies a patient's situation into a triage care level."""
    return {"symptoms": symptoms, "pain_scale": pain_scale, "duration_hours": duration_hours, "age": age, "has_chronic_conditions": has_chronic_conditions}

def get_nearest_care_facility(care_level: str, location_hint: str = "not provided") -> dict:
    """Returns appropriate care facility and contact guidance based on triage level."""
    routing = {
        "EMERGENCY":   {"facility": "Emergency Room / 911", "action": "Call 911 or go to the nearest ER immediately.", "time_guidance": "Within 15 minutes."},
        "URGENT_CARE": {"facility": "Urgent Care Center", "action": "Go to the nearest urgent care clinic. Walk-in. Bring insurance card.", "time_guidance": "Within 2-4 hours."},
        "APPOINTMENT": {"facility": "Primary Care / GP", "action": "Call your doctor to book an appointment.", "time_guidance": "Within 24-48 hours."},
        "SELF_CARE":   {"facility": "Home / Telehealth", "action": "Monitor at home. Rest, stay hydrated.", "time_guidance": "Re-evaluate in 24-48 hours."},
    }
    result = routing.get(care_level, routing["SELF_CARE"]).copy()
    result["location_hint"] = location_hint
    return result

def check_red_flag_symptoms(symptoms: str) -> dict:
    """Screens for absolute red-flag symptoms requiring immediate 911/ER."""
    return {"symptoms_to_screen": symptoms}

root_agent = Agent(
    name="medical_triage_agent",
    model="gemini-2.5-flash",
    description="Medical triage AI that classifies symptoms and routes to correct care level.",
    instruction="""You are MedAI, an AI medical triage assistant.

Assess symptoms and route to: EMERGENCY, URGENT_CARE, APPOINTMENT, or SELF_CARE.

Steps:
1. Call check_red_flag_symptoms — if red flag found → EMERGENCY immediately
   Red flags: chest pain, breathing difficulty, stroke signs (face drooping, arm weakness, slurred speech), severe allergic reaction, uncontrolled bleeding, loss of consciousness, seizure, worst headache of life, sepsis signs, suicidal ideation

2. Call classify_triage_level with patient data:
   EMERGENCY = pain >=9 or red flag
   URGENT_CARE = pain 6-8 or rapid worsening or high-risk (age>65, chronic conditions)
   APPOINTMENT = pain 3-5, stable, needs evaluation
   SELF_CARE = pain 0-2, minor symptoms

3. Call get_nearest_care_facility with the level.

4. Reply with:
   - Care level emoji + label: 🚨 EMERGENCY | ⚠️ URGENT CARE | 📅 SEE A DOCTOR | 🏠 SELF-CARE
   - Why this level was chosen (2-3 sentences)
   - Exact next steps
   - 3-5 warning signs to watch for
   - End with: ⚕️ This is AI-assisted triage only. Not a substitute for professional medical advice.""",
    tools=[classify_triage_level, get_nearest_care_facility, check_red_flag_symptoms],
)
