# proofreader_agent.py
from fastapi import FastAPI, UploadFile, Form, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import tempfile, os, re, traceback
import httpx

from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from chat_router_proofreader import chat_router

# ──────────────────────── App Init ────────────────────────
app = FastAPI(debug=True)
app.include_router(chat_router)

# ──────────────────────── Prompt Templates ────────────────────────
manual_template = """
{instructions}

You are a professional proofreader. Proofread the following text and:
1. Correct grammar and spelling
2. Fix punctuation
3. Improve clarity while preserving meaning
4. Return the corrected text first, then a bullet list of notable changes

Text:
{text}

Respond exactly in this format:
Corrected text:
[Your corrected version]

===END_CORRECTED===
Changes made:
[List of changes]

===END_CHANGES===
"""

pdf_template = """
{instructions}

You are a professional proofreader. This is a raw text extracted from a student-submitted PDF.
Please ignore layout formatting issues and focus on:
1. Correct grammar and spelling
2. Fix punctuation
3. Improve clarity

Text:
{text}

Respond in this format:
Corrected text:
[Your corrected version]

===END_CORRECTED===
Changes made:
[List of changes]

===END_CHANGES===
"""

# ──────────────────────── LangChain Setup ────────────────────────
model = Ollama(model="gemma3:1b")
manual_prompt = ChatPromptTemplate.from_template(manual_template)
pdf_prompt = ChatPromptTemplate.from_template(pdf_template)

# ──────────────────────── Profiles ────────────────────────
PROFILES = {
    "academic": {
        "instructions": "Use a formal academic tone. Avoid contractions and colloquialisms."
    },
    "casual": {
        "instructions": "Use a casual, conversational tone. Contractions are fine."
    },
    "concise": {
        "instructions": "Be as brief as possible while keeping meaning intact."
    }
}

# ──────────────────────── Request Model ────────────────────────
class ProofreaderRequest(BaseModel):
    user_id: int
    profile: Optional[str] = Form(None)
    input_type: str  # 'text' | 'pdf'
    text: str = ""
    mode: str = "manual"  # 'manual' | 'pdf' | 'chat'
    history: str = "[]"
    message_id: int = Form(...)

    @classmethod
    def as_form(
        cls,
        user_id: int = Form(...),
        profile: Optional[str] = Form(None),
        input_type: str = Form(...),
        text: str = Form(""),
        mode: str = Form("manual"),
        history: str = Form("[]"),
        message_id: int = Form(...)
    ):
        return cls(
            user_id=user_id,
            profile=profile,
            input_type=input_type,
            text=text,
            mode=mode,
            history=history,
            message_id=message_id
        )

# ──────────────────────── Helpers ────────────────────────
def extract_text_from_pdf(path: str) -> str:
    loader = PyPDFLoader(path)
    pages = loader.load()
    return " ".join(p.page_content for p in pages[:2])

def clean_output(text: str) -> str:
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"^\s*[\*\-]\s*", "", text, flags=re.MULTILINE)
    return text.strip()

async def generate_output(profile, input_type, text="", pdf_file: UploadFile = None):
    if input_type == "pdf":
        if not pdf_file:
            raise ValueError("PDF file is required but not provided.")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            contents = await pdf_file.read()
            tmp.write(contents)
            tmp_path = tmp.name
        text = extract_text_from_pdf(tmp_path)
        prompt = pdf_prompt
    else:
        if not text.strip():
            raise ValueError("No text provided.")
        prompt = manual_prompt

    instructions = PROFILES.get(profile, {}).get("instructions", "")
    user_input = {"instructions": instructions, "text": text}
    chain = prompt | model
    result = chain.invoke(user_input)
    return clean_output(result)

# ──────────────────────── Endpoint ────────────────────────
@app.post("/proofreader")
async def proofreader_endpoint(
    data: ProofreaderRequest = Depends(ProofreaderRequest.as_form),
    pdf_file: Optional[UploadFile] = None,
    request: Request = None
):
    try:
        if data.mode in ("manual", "pdf") and not data.profile:
            raise HTTPException(status_code=400, detail="Profile is required.")

        if data.mode == "chat":
            async with httpx.AsyncClient(timeout=None) as client:
                chat_url = "http://127.0.0.1:5002/proofread_chat"  # or your port
                resp = await client.post(chat_url, data={
                    "text": data.text,
                    "user_id": str(data.user_id),
                    "db_message_id": str(data.message_id)
                })
                resp.raise_for_status()
                return resp.json()

        # For 'manual' and 'pdf'
        output = await generate_output(
            profile=data.profile,
            input_type=data.input_type,
            text=data.text,
            pdf_file=pdf_file
        )

        try:
            corrected = output.split("Corrected text:")[1].split("===END_CORRECTED===")[0]
            changes = output.split("Changes made:")[1].split("===END_CHANGES===")[0]
        except Exception:
            corrected, changes = output, ""

        return {
            "corrected": clean_output(corrected),
            "changes": clean_output(changes)
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": str(e), "trace": traceback.format_exc()}
        )
