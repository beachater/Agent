from fastapi import FastAPI, HTTPException, UploadFile, Form # type: ignore
from fastapi.responses import JSONResponse # type: ignore
from pydantic import BaseModel, ValidationError # type: ignore
from langchain_community.llms import Ollama # type: ignore
from langchain_core.prompts import ChatPromptTemplate # type: ignore
from langchain_community.document_loaders.pdf import PyPDFLoader # type: ignore
import shutil, os, re, tempfile, uvicorn, traceback # type: ignore

manual_topic_template = """
You are an experienced and friendly virtual tutor who helps students understand academic topics clearly and effectively.

Your goal is to explain the topic in a way that matches the student's grade level and learning needs.

Parameters:
- Learning type: {learning_type}
- Topic: {topic}

Instructions:
- Provide a detailed explanation of the topic.
- Use examples, analogies, or simple breakdowns appropriate for the student's grade level.
- Address any specific learning needs or context provided.
- Do NOT just define terms — aim to build understanding.
- summarize — explain thoroughly.
- Use clear language, step-by-step logic, and relevant examples.
- Adapt your explanation based on any additional learning notes provided.

Respond ONLY with the explanation text (no extra commentary).
"""

pdf_topic_template = """
You are a knowledgeable and supportive virtual tutor.

You will receive content extracted from a textbook or document (such as a PDF). Your task is to explain this content in a way that is understandable to a student at the given grade level.

Parameters:
- Learning type: {learning_type}
- Extracted Content: {topic}

Instructions:
- Provide a detailed explanation of the topic.
- Use examples, analogies, or simple breakdowns appropriate for the student's grade level.
- Address any specific learning needs or context provided.
- Do NOT just define terms — aim to build understanding.
- Do NOT summarize — explain thoroughly.
- Use clear language, step-by-step logic, and relevant examples.
- Adapt your explanation based on any additional learning notes provided.

Respond ONLY with the explanation text (no extra commentary).
"""

model = Ollama(model="llama3")
manual_prompt = ChatPromptTemplate.from_template(manual_topic_template)
pdf_prompt = ChatPromptTemplate.from_template(pdf_topic_template)

class RewriterInput(BaseModel):
    input_type: str = ""
    pdf_path: str = ""
    learning_type: str

def load_pdf_content(pdf_path: str) -> str:
    if not os.path.exists(pdf_path):
        raise FileNotFoundError("PDF file not found.")
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    return "\n".join(doc.page_content for doc in documents)

# Function to clean the output from formatting artifacts
def clean_output(text: str) -> str:
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"^\s*[\*\-]\s*", "", text, flags=re.MULTILINE)
    return text.strip()

def generate_output(input_type: str, pdf_path: str =  "", learner_type: str = "") -> str:
    if input_type == "pdf":
        topic = load_pdf_content(pdf_path)
        prompt = pdf_prompt
    else:
        topic = input_type  # ← manual topic entered directly
        prompt = manual_prompt

    # Compose input dict for prompt
    prompt_input = {
        "learner_type": learner_type,
        "topic": topic
    }

    chain = prompt | model
    result = chain.invoke(prompt_input)
    return clean_output(result)

app = FastAPI()

@app.post("/rewriter")
async def rewriter_api(input: RewriterInput):
    try:
        output = generate_output(
            input_type=input.input_type,
            pdf_path=input.pdf_path,
            learner_type=input.learner_type
        )
        return {"output": output}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.errors())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("rewriter_agent:app", host="127.0.0.1", port=5001, reload=True)