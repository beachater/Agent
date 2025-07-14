# sentence_starters_agent.py
from fastapi import FastAPI, Form, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import httpx

from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# ───────────────── App Init ─────────────────
app = FastAPI(debug=True)

# ─────────────── Grade Profiles ───────────────
GRADE_LEVEL_PROFILES = {
    "kindergarten": {
        "instructions": "Use very simple words and phrases. Focus on curiosity and helping the child describe basic things.",
    },
    "elementary": {
        "instructions": "Use clear and easy words. Help the student begin sentences that describe, explain, or share ideas clearly.",
    },
    "junior high": {
        "instructions": "Use age-appropriate vocabulary. Help the student write more detailed ideas and opinions.",
    },
    "senior high": {
        "instructions": "Use more formal phrasing. Encourage thoughtful analysis, opinions, or comparisons.",
    },
    "college": {
        "instructions": "Use academic tone. Encourage critical thinking, argument development, or synthesis of ideas.",
    }
}
DEFAULT_MODEL = "gemma3"

# ─────────────── Request Model ───────────────
class SentenceStarterRequest(BaseModel):
    grade_level: str
    topic: str
    mode: str = "manual"       # 'manual' | 'chat'
    history: str = "[]"        # JSON‑encoded chat history
    message_id: int            # for chat DB

    @classmethod
    def as_form(
        cls,
        grade_level: str = Form(...),
        topic: str = Form(...),
        mode: str = Form("manual"),
        history: str = Form("[]"),
        message_id: int = Form(...)
    ):
        return cls(
            grade_level=grade_level,
            topic=topic,
            mode=mode,
            history=history,
            message_id=message_id
        )

# ─────────────── Helpers ───────────────
def build_prompt(grade_level: str, topic: str) -> str:
    profile = GRADE_LEVEL_PROFILES.get(grade_level.lower())
    if not profile:
        raise ValueError(f"Unknown grade level: {grade_level}")
    instr = profile["instructions"]
    return f"""
You are an AI writing coach for {grade_level} students. {instr}

Topic: "{topic}"

Guidelines:
- Generate exactly 5 sentence starters.
- Each should start naturally, like how a student would open a paragraph.
- Do NOT finish the thought or write a complete sentence.
- Must be open‑ended and avoid repetitive phrases.
- Adapt tone and vocabulary for the grade level.
- Return each starter on its own line with no numbering, bullets, or extra commentary.
"""

def extract_starters(raw: str) -> List[str]:
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    return lines[:5]

async def generate_starters(grade_level: str, topic: str) -> List[str]:
    prompt_text = build_prompt(grade_level, topic)
    prompt = ChatPromptTemplate.from_template(prompt_text)
    model = OllamaLLM(model=DEFAULT_MODEL)
    chain = prompt | model
    result = chain.invoke({})
    return extract_starters(result)

# ─────────────── Endpoint ───────────────
@app.post("/sentencestarters")
async def sentence_starters_endpoint(
    data: SentenceStarterRequest = Depends(SentenceStarterRequest.as_form),
    request: Request = None
):
    try:
        if data.mode == "chat":
            # forward to your chat‑history service
            async with httpx.AsyncClient(timeout=None) as client:
                chat_url = "http://127.0.0.1:5002/sentencestarters_chat"
                resp = await client.post(chat_url, data={
                    "grade_level": data.grade_level,
                    "topic": data.topic,
                    "history": data.history,
                    "db_message_id": str(data.message_id)
                })
                resp.raise_for_status()
                return resp.json()

        # manual mode: generate fresh starters
        starters = await generate_starters(data.grade_level, data.topic)
        if len(starters) < 5:
            raise HTTPException(500, f"Expected 5 starters, got {len(starters)}")

        return {"starters": starters}

    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )
