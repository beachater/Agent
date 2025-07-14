# real_world_agent.py
from fastapi import FastAPI, Form, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import httpx

from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# ───────────────── App Init ─────────────────
app = FastAPI(debug=True)

# ─────────────── Request Model ───────────────
class RealWorldRequest(BaseModel):
    grade_level: str
    topic: str
    mode: str = "manual"      # 'manual' | 'chat'
    history: str = "[]"       # JSON‑encoded chat history
    message_id: int           # for chat DB

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
    return f"""
You're an educational AI expert helping students relate what they're learning to real‑world applications.

Generate 2–3 real‑world examples or applications of this topic:
\"{topic}\"
for a student in {grade_level}. Focus on relevance, clarity, and practical context.

Start each example with a short bolded title (e.g., **Solar Panels**), followed by a concise paragraph explaining the connection.
Do not include extra commentary or numbering.
"""

def extract_examples(raw: str) -> List[str]:
    # Split on two or more newlines to separate examples
    parts = [part.strip() for part in raw.split("\n\n") if part.strip()]
    return parts[:3]

async def generate_examples(grade_level: str, topic: str) -> List[str]:
    instructions = build_prompt(grade_level, topic)
    model = OllamaLLM(model="gemma3:1b")
    chain = ChatPromptTemplate.from_template(instructions) | model
    result = chain.invoke({})
    return extract_examples(result)

# ─────────────── Endpoint ───────────────
@app.post("/realworld")
async def real_world_endpoint(
    data: RealWorldRequest = Depends(RealWorldRequest.as_form),
    request: Request = None
):
    try:
        if data.mode == "chat":
            # forward to your chat‑history service
            async with httpx.AsyncClient(timeout=None) as client:
                chat_url = "http://127.0.0.1:5002/realworld_chat"
                resp = await client.post(chat_url, data={
                    "grade_level": data.grade_level,
                    "topic": data.topic,
                    "history": data.history,
                    "db_message_id": str(data.message_id)
                })
                resp.raise_for_status()
                return resp.json()

        # manual mode: generate fresh examples
        examples = await generate_examples(data.grade_level, data.topic)
        if not examples:
            raise HTTPException(500, "No examples generated.")

        return {"examples": examples}

    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )
