# study_habits_agent.py
from fastapi import FastAPI, Form, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import httpx

from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# ───────────────── App Init ─────────────────
app = FastAPI(debug=True)

# ─────────────── Grade Profiles ───────────────
GRADE_PROFILES = {
    "kindergarten": "Use playful, simple words. Focus on routines, fun learning moments, and positive reinforcement. Keep sessions short and colorful.",
    "elementary":   "Use friendly and fun language. Break tasks into small steps. Focus on creating habits, using visual aids, and celebrating effort.",
    "junior high":  "Use engaging and relatable tone. Encourage organization, self-motivation, and balancing school and personal life.",
    "senior high":  "Use mature, focused advice. Address time management, review techniques, and subject-specific strategies.",
    "college":      "Use academic tone. Focus on deep learning, exam strategy, scheduling, and productivity systems like Pomodoro or spaced repetition."
}

DEFAULT_MODEL = "gemma3:1b"

# ─────────────── Request Model ───────────────
class StudyHabitsRequest(BaseModel):
    grade_level: str
    goal: str
    mode: str = "manual"       # 'manual' | 'chat'
    history: str = "[]"        # JSON‑encoded chat history
    message_id: int            # for chat DB

    @classmethod
    def as_form(
        cls,
        grade_level: str = Form(...),
        goal: str = Form(...),
        mode: str = Form("manual"),
        history: str = Form("[]"),
        message_id: int = Form(...)
    ):
        return cls(
            grade_level=grade_level,
            goal=goal,
            mode=mode,
            history=history,
            message_id=message_id
        )

# ─────────────── Helpers ───────────────
def build_prompt(grade_level: str, goal: str) -> str:
    profile = GRADE_PROFILES.get(
        grade_level.lower(),
        "Use clear, student-friendly language appropriate for the grade level."
    )
    return f"""
You are a smart AI tutor.

Your task is to generate a practical, organized, and motivational study plan for a {grade_level} student.
The student's preparation goal is:
"{goal}"

Student Profile: {profile}

Instructions:
- Look for any time-related phrases in the goal (e.g., "exam in 3 days", "test next week").
  • If a timeframe is specified, tailor each day to that timeframe exactly.
  • If none is specified, create a 2–3 week plan based on topic complexity.
- Format:
  • For multi-week plans:
      Week 1: Title
        Day 1 – Topic (duration)
          Activity: …
          Review: …
          Tool: …
      … 
  • For short plans (3–5 days):
      Day 1 – Topic (duration)
        Activity: …
        Review: …
        Tool: …
- Always include 1 rest day if the plan spans 5 days or more.
- Use plain formatting (no markdown symbols). Keep it structured and readable.
- End with an encouraging sentence (no “Final Note” heading).
"""

async def generate_plan(grade_level: str, goal: str) -> str:
    prompt_text = build_prompt(grade_level, goal)
    prompt = ChatPromptTemplate.from_template(prompt_text)
    model = OllamaLLM(model=DEFAULT_MODEL)
    chain = prompt | model
    result = chain.invoke({})
    return result.strip()

# ─────────────── Endpoint ───────────────
@app.post("/studyhabits")
async def study_habits_endpoint(
    data: StudyHabitsRequest = Depends(StudyHabitsRequest.as_form),
    request: Request = None
):
    try:
        if data.mode == "chat":
            # forward to your chat‑history service
            async with httpx.AsyncClient(timeout=None) as client:
                chat_url = "http://127.0.0.1:5002/studyhabits_chat"
                resp = await client.post(chat_url, data={
                    "grade_level": data.grade_level,
                    "goal": data.goal,
                    "history": data.history,
                    "db_message_id": str(data.message_id)
                })
                resp.raise_for_status()
                return resp.json()

        # manual mode: generate fresh study plan
        plan = await generate_plan(data.grade_level, data.goal)
        if not plan:
            raise HTTPException(500, "Failed to generate a study plan.")

        return {"plan": plan}

    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )
