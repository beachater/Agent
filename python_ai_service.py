from fastapi import FastAPI, UploadFile, File, Form
import shutil
import os
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders.pdf import PyPDFLoader

template = """
You are an assistant who explains book content in a way suitable for the learner.

Parameters:
- Grade level: {grade_level}
- Learning speed: {learning_speed}

Task:
Based on the input text below, provide a clear, detailed explanation that matches the learner's grade level and learning speed.

Do NOT summarize the text. Instead, explain the content thoroughly, using examples or simple language if needed to make it easier to understand.

Input text: "{context}"

Respond ONLY with the explanation text (no extra text).
"""

model = Ollama(model="llama3")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

def get_adaptive_content(context: str, grade_level: str, learning_speed: str) -> str:
    return chain.invoke({
        "context": context,
        "grade_level": grade_level,
        "learning_speed": learning_speed
    })

def load_pdf_content(pdf_path: str) -> str:
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    return "\n".join(doc.page_content for doc in documents)

app = FastAPI()

@app.post("/adaptive-content/")
async def adaptive_content(
    input_text: str = Form(""),
    grade_level: str = Form(...),
    learning_speed: str = Form(...),
    pdf: UploadFile = File(None)
):
    context = input_text
    if pdf:
        temp_path = f"/tmp/{pdf.filename}"
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(pdf.file, f)
        context = load_pdf_content(temp_path)
        os.remove(temp_path)

    result = get_adaptive_content(context, grade_level, learning_speed)
    return {"adaptive_content": result}
