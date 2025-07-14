# main.py

from fastapi import FastAPI, Form, Depends, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import tempfile, re, traceback
import httpx

from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader
# from chat_router_proofreader import chat_router  # your existing proofread chat router

app = FastAPI(debug=True)

# ──────────── Shared Models & Helpers ────────────

# —— Proofreader templates & profiles —— #
# manual_template = """
# {instructions}

# You are a professional proofreader. Proofread the following text and:
# 1. Correct grammar and spelling
# 2. Fix punctuation
# 3. Improve clarity while preserving meaning
# 4. Return the corrected text first, then a bullet list of notable changes

# Text:
# {text}

# Respond exactly in this format:
# Corrected text:
# [Your corrected version]

# ===END_CORRECTED===
# Changes made:
# [List of changes]

# ===END_CHANGES===
# """

# pdf_template = """
# {instructions}

# You are a professional proofreader. This is a raw text extracted from a student-submitted PDF.
# Please ignore layout formatting issues and focus on:
# 1. Correct grammar and spelling
# 2. Fix punctuation
# 3. Improve clarity

# Text:
# {text}

# Respond in this format:
# Corrected text:
# [Your corrected version]

# ===END_CORRECTED===
# Changes made:
# [List of changes]

# ===END_CHANGES===
# """

# PROFILES = {
#     "academic":    {"instructions": "Use a formal academic tone. Avoid contractions and colloquialisms."},
#     "casual":      {"instructions": "Use a casual, conversational tone. Contractions are fine."},
#     "concise":     {"instructions": "Be as brief as possible while keeping meaning intact."}
# }

# def clean_output(text: str) -> str:
#     text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
#     text = re.sub(r"\*(.*?)\*", r"\1", text)
#     text = re.sub(r"^\s*[\*\-]\s*", "", text, flags=re.MULTILINE)
#     return text.strip()

# def extract_text_from_pdf(path: str) -> str:
#     loader = PyPDFLoader(path)
#     pages = loader.load()
#     return " ".join(p.page_content for p in pages[:2])

# async def generate_proofreader(profile, input_type, text="", pdf_file: UploadFile = None):
#     if input_type == "pdf":
#         if not pdf_file:
#             raise ValueError("PDF file is required.")
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
#             tmp.write(await pdf_file.read())
#             tmp_path = tmp.name
#         text = extract_text_from_pdf(tmp_path)
#         prompt = ChatPromptTemplate.from_template(pdf_template)
#     else:
#         if not text.strip():
#             raise ValueError("No text provided.")
#         prompt = ChatPromptTemplate.from_template(manual_template)

#     instructions = PROFILES.get(profile, {}).get("instructions", "")
#     user_input = {"instructions": instructions, "text": text}

#     chain = prompt | OllamaLLM(model="gemma3:1b")
#     result = chain.invoke(user_input)
#     return clean_output(result)

# —— Five Questions —— #
GRADE_Q_PROFILES = {
    "kindergarten": "Keep language playful for a 5-year-old…",
    "elementary":   "Friendly, clear for ages 6–10…",
    "junior high":  "Relatable for ages 11–14…",
    "senior high":  "Thoughtful for ages 15–18…",
    "college":      "Academic and precise…"
}

def build_questions_prompt(level: str, topic: str) -> str:
    profile = GRADE_Q_PROFILES.get(level.lower(), "")
    return f"""
You are a helpful AI that creates thoughtful, open-ended questions…

Generate exactly five unique, deep, age-appropriate questions on:
\"{topic}\"
Audience: {level}
Profile: {profile}

- Open-ended only (no yes/no).
- Number them 1–5, nothing else.
"""

def extract_questions(raw: str) -> List[str]:
    matches = re.findall(r"\b\d\.\s+(.*?)(?=\n\d\.|\Z)", raw, flags=re.DOTALL)
    return [m.strip() for m in matches][:5]

async def generate_questions(level: str, topic: str):
    prompt = ChatPromptTemplate.from_template(build_questions_prompt(level, topic))
    result = (prompt | OllamaLLM(model="gemma3")).invoke({})
    return extract_questions(result)

# —— Real World Examples —— #
def build_realworld_prompt(level: str, topic: str) -> str:
    return f"""
You're an educational AI expert…
Generate 2–3 real-world examples for "{topic}" for a {level} student.
Start each with a bold title (e.g., **Title**), then a short paragraph.
"""

def extract_examples(raw: str) -> List[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", raw) if p.strip()][:3]

async def generate_examples(level: str, topic: str):
    prompt = ChatPromptTemplate.from_template(build_realworld_prompt(level, topic))
    result = (prompt | OllamaLLM(model="gemma3:1b")).invoke({})
    return extract_examples(result)

# —— Sentence Starters —— #
GRADE_S_PROFILES = {
    "kindergarten":  "Use very simple words…",
    "elementary":    "Clear and easy words…",
    "junior high":   "Age-appropriate vocabulary…",
    "senior high":   "More formal phrasing…",
    "college":       "Academic tone…"
}

def build_starters_prompt(level: str, topic: str) -> str:
    instr = GRADE_S_PROFILES.get(level.lower()) or ""
    return f"""
You are an AI coach for {level} students. {instr}
Topic: "{topic}"
Generate exactly 5 open-ended sentence starters, one per line, no bullets or numbering.
"""

def extract_starters(raw: str) -> List[str]:
    return [l.strip() for l in raw.splitlines() if l.strip()][:5]

async def generate_starters(level: str, topic: str):
    prompt = ChatPromptTemplate.from_template(build_starters_prompt(level, topic))
    result = (prompt | OllamaLLM(model="gemma3")).invoke({})
    return extract_starters(result)

# —— Study Habits —— #
GRADE_H_PROFILES = {
    "kindergarten": "Use playful…",
    "elementary":   "Friendly…",
    "junior high":  "Engaging…",
    "senior high":  "Mature…",
    "college":      "Academic…"
}

def build_study_prompt(level: str, goal: str) -> str:
    profile = GRADE_H_PROFILES.get(level.lower(), "")
    return f"""
You are a smart AI tutor…
Generate a structured study plan for a {level} student whose goal is "{goal}".
Follow the timeframe in the goal (e.g., “3 days”), or default to a 2–3 week plan.
Plain formatting; include rest days; end with encouragement.
"""

async def generate_plan(level: str, goal: str):
    prompt = ChatPromptTemplate.from_template(build_study_prompt(level, goal))
    result = (prompt | OllamaLLM(model="gemma3:1b")).invoke({})
    return result.strip()

# ──────────── Routers & Endpoints ────────────

# Proofreader
# app.include_router(chat_router)  # your chat-history router

# class ProofReq(BaseModel):
#     user_id: int
#     profile: Optional[str]
#     input_type: str
#     text: str = ""
#     mode: str = "manual"
#     history: str = "[]"
#     message_id: int

#     @classmethod
#     def as_form(cls, user_id: int = Form(...), profile: Optional[str] = Form(None),
#                 input_type: str = Form(...), text: str = Form(""),
#                 mode: str = Form("manual"), history: str = Form("[]"),
#                 message_id: int = Form(...)):
#         return cls(user_id=user_id, profile=profile, input_type=input_type,
#                    text=text, mode=mode, history=history, message_id=message_id)

# @app.post("/proofreader")
# async def proofreader_endpoint(
#     data: ProofReq = Depends(ProofReq.as_form),
#     pdf_file: Optional[UploadFile] = None
# ):
#     try:
#         if data.mode == "chat":
#             async with httpx.AsyncClient(timeout=None) as client:
#                 resp = await client.post(
#                     "http://127.0.0.1:5002/proofread_chat",
#                     data={"text": data.text, "user_id": data.user_id, "db_message_id": data.message_id}
#                 )
#                 resp.raise_for_status()
#                 return resp.json()

#         if not data.profile:
#             raise HTTPException(400, "Profile is required.")
#         out = await generate_proofreader(data.profile, data.input_type, data.text, pdf_file)
#         try:
#             corrected = out.split("Corrected text:")[1].split("===END_CORRECTED===")[0]
#             changes   = out.split("Changes made:")[1].split("===END_CHANGES===")[0]
#         except:
#             corrected, changes = out, ""
#         return {"corrected": clean_output(corrected), "changes": clean_output(changes)}

#     except Exception as e:
#         return JSONResponse(500, {"detail": str(e), "trace": traceback.format_exc()})

# Five Questions
class FiveQReq(BaseModel):
    grade_level: str
    prompt: str
    mode: str = "manual"
    history: str = "[]"
    message_id: int

    @classmethod
    def as_form(cls, grade_level: str = Form(...), prompt: str = Form(...),
                mode: str = Form("manual"), history: str = Form("[]"),
                message_id: int = Form(...)):
        return cls(grade_level=grade_level, prompt=prompt,
                   mode=mode, history=history, message_id=message_id)

@app.post("/fivequestions")
async def fivequestions_endpoint(data: FiveQReq = Depends(FiveQReq.as_form)):
    try:
        if data.mode == "chat":
            async with httpx.AsyncClient(timeout=None) as client:
                resp = await client.post("http://127.0.0.1:5002/fiveq_chat", data={
                    "grade_level": data.grade_level,
                    "prompt": data.prompt,
                    "history": data.history,
                    "db_message_id": data.message_id
                })
                resp.raise_for_status()
                return resp.json()

        qs = await generate_questions(data.grade_level, data.prompt)
        if len(qs) < 5:
            raise HTTPException(500, f"Expected 5, got {len(qs)}")
        return {"questions": qs}

    except Exception as e:
        return JSONResponse(500, {"detail": str(e)})

# Real World
class RWReq(BaseModel):
    grade_level: str
    topic: str
    mode: str = "manual"
    history: str = "[]"
    message_id: int

    @classmethod
    def as_form(cls, grade_level: str = Form(...), topic: str = Form(...),
                mode: str = Form("manual"), history: str = Form("[]"),
                message_id: int = Form(...)):
        return cls(grade_level=grade_level, topic=topic,
                   mode=mode, history=history, message_id=message_id)

@app.post("/realworld")
async def realworld_endpoint(data: RWReq = Depends(RWReq.as_form)):
    try:
        if data.mode == "chat":
            async with httpx.AsyncClient(timeout=None) as client:
                resp = await client.post("http://127.0.0.1:5002/realworld_chat", data={
                    "grade_level": data.grade_level,
                    "topic": data.topic,
                    "history": data.history,
                    "db_message_id": data.message_id
                })
                resp.raise_for_status()
                return resp.json()

        ex = await generate_examples(data.grade_level, data.topic)
        if not ex: raise HTTPException(500, "No examples")
        return {"examples": ex}

    except Exception as e:
        return JSONResponse(500, {"detail": str(e)})

# Sentence Starters
class StarterReq(BaseModel):
    grade_level: str
    topic: str
    mode: str = "manual"
    history: str = "[]"
    message_id: int

    @classmethod
    def as_form(cls, grade_level: str = Form(...), topic: str = Form(...),
                mode: str = Form("manual"), history: str = Form("[]"),
                message_id: int = Form(...)):
        return cls(grade_level=grade_level, topic=topic,
                   mode=mode, history=history, message_id=message_id)

@app.post("/sentencestarters")
async def starters_endpoint(data: StarterReq = Depends(StarterReq.as_form)):
    try:
        if data.mode == "chat":
            async with httpx.AsyncClient(timeout=None) as client:
                resp = await client.post("http://127.0.0.1:5002/sentencestarters_chat", data={
                    "grade_level": data.grade_level,
                    "topic": data.topic,
                    "history": data.history,
                    "db_message_id": data.message_id
                })
                resp.raise_for_status()
                return resp.json()

        sts = await generate_starters(data.grade_level, data.topic)
        if len(sts) < 5: raise HTTPException(500, f"Expected 5, got {len(sts)}")
        return {"starters": sts}

    except Exception as e:
        return JSONResponse(500, {"detail": str(e)})

# Study Habits
class StudyReq(BaseModel):
    grade_level: str
    goal: str
    mode: str = "manual"
    history: str = "[]"
    message_id: int

    @classmethod
    def as_form(cls, grade_level: str = Form(...), goal: str = Form(...),
                mode: str = Form("manual"), history: str = Form("[]"),
                message_id: int = Form(...)):
        return cls(grade_level=grade_level, goal=goal,
                   mode=mode, history=history, message_id=message_id)

@app.post("/studyhabits")
async def study_endpoint(data: StudyReq = Depends(StudyReq.as_form)):
    try:
        if data.mode == "chat":
            async with httpx.AsyncClient(timeout=None) as client:
                resp = await client.post("http://127.0.0.1:5002/studyhabits_chat", data={
                    "grade_level": data.grade_level,
                    "goal": data.goal,
                    "history": data.history,
                    "db_message_id": data.message_id
                })
                resp.raise_for_status()
                return resp.json()

        plan = await generate_plan(data.grade_level, data.goal)
        if not plan: raise HTTPException(500, "No plan generated.")
        return {"plan": plan}

    except Exception as e:
        return JSONResponse(500, {"detail": str(e)})
