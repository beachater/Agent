# five_question_agent.py
from fastapi import FastAPI, Form, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import httpx
import re
import json # Ensure json is imported for potential history parsing

from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# Import the new router
from five_question_router import five_question_router # Assuming it's in the same directory

# ───────────────── App Init ─────────────────
app = FastAPI(debug=True)

# Include the five_question_router
app.include_router(five_question_router)

# ──────────────── Grade Profiles ────────────────
GRADE_PROFILES = {
    "kindergarten": "Keep the language extremely simple and use playful, imaginative words that a 5-year-old can understand. Focus on feelings, colors, and basic choices.",
    "elementary":   "Use friendly and clear language suitable for children aged 6 to 10. Encourage curiosity and basic reasoning, like 'why' and 'how' questions.",
    "junior high":  "Write with a bit more depth for students aged 11 to 14. Encourage connections to real life or personal experience.",
    "senior high":  "Use thoughtful and mature language for students aged 15 to 18. Encourage analytical thinking, ethical reasoning, and creative problem-solving.",
    "college":      "Use academic, mature, and precise language. Encourage synthesis, debate, and deep exploration of ideas."
}

# ─────────────── Request Model ───────────────
class FiveQuestionRequest(BaseModel):
    grade_level: str
    prompt: str # This is the main topic for manual mode, or the user's current message for chat mode
    user_id: int # Add user_id here as it's needed for chat history
    mode: str = "manual"        # 'manual' | 'chat'
    history: str = "[]"         # JSON‑encoded chat history (router handles persistence)
    message_id: int             # for chat DB

    @classmethod
    def as_form(
        cls,
        grade_level: str = Form(...),
        prompt: str = Form(...),
        user_id: int = Form(...), # Include in form dependency
        mode: str = Form("manual"),
        history: str = Form("[]"),
        message_id: int = Form(...)
    ):
        return cls(
            grade_level=grade_level,
            prompt=prompt,
            user_id=user_id,
            mode=mode,
            history=history,
            message_id=message_id
        )

# ─────────────── Helpers ───────────────
def build_prompt(grade_level: str, topic: str) -> str:
    profile = GRADE_PROFILES.get(grade_level.lower(), "Use plain, student-friendly language.")
    return f"""
You are a helpful AI that creates thoughtful, open-ended questions to promote critical thinking.

Generate exactly five unique, deep, and age-appropriate questions on the topic: "{topic}"
Audience: {grade_level}
Profile: {profile}

Guidelines:
- Open-ended (no yes/no).
- Encourage reflection, analysis, or creative thinking.
- No factual-quiz or multiple-choice style.

Output format (nothing else):
1.
2.
3.
4.
5.
"""

def extract_questions(raw: str) -> List[str]:
    pattern = r"\b\d\.\s+(.*?)(?=\n\d\.|\Z)"
    questions = re.findall(pattern, raw, flags=re.DOTALL)
    return [q.strip() for q in questions][:5]

async def generate_questions(grade_level: str, topic: str) -> List[str]:
    instructions = build_prompt(grade_level, topic)
    model = OllamaLLM(model="gemma3")
    chain = ChatPromptTemplate.from_template(instructions) | model
    result = chain.invoke({})
    return extract_questions(result)

# ─────────────── Endpoint ───────────────
@app.post("/fivequestions")
async def five_question_endpoint(
    data: FiveQuestionRequest = Depends(FiveQuestionRequest.as_form),
    request: Request = None
):
    try:
        if data.mode == "chat":
            # forward to your chat router for history integration
            async with httpx.AsyncClient(timeout=None) as client:
                # The URL for the router endpoint within the same application
                chat_url = "http://127.0.0.1:8000/fiveq_chat" # Assuming main app runs on port 8000
                print(f"[DEBUG] Forwarding to chat router: Current Message='{data.prompt}' (User ID: {data.user_id}, Message ID: {data.message_id})")
                resp = await client.post(chat_url, data={
                    "grade_level": data.grade_level,
                    "prompt": data.prompt, # This is the original topic or current context
                    "current_message": data.prompt, # The actual latest message from the user
                    "user_id": str(data.user_id),
                    "db_message_id": str(data.message_id)
                })
                resp.raise_for_status()
                return resp.json()

        # manual mode: generate fresh questions
        questions = await generate_questions(data.grade_level, data.prompt)
        if len(questions) < 5:
            raise HTTPException(500, f"Expected 5 questions, but got {len(questions)}")

        return {"questions": questions}

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback_str = traceback.format_exc()
        print(f"[Five Question Agent Error] {e}\n{traceback_str}")
        return JSONResponse(
            status_code=500,
            content={"detail": str(e), "trace": traceback_str}
        )