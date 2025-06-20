import os
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader

# Create FastAPI app
app = FastAPI()

# Prompt templates
manual_topic_template = """
You are an experienced and friendly virtual tutor. Your goal is to rewrite educational content based on the student's learning level.

- Learning level: {learning_type}
- Topic: {input_type}

Please rewrite the above topic to make it more suitable and easier to understand for this specific learner type.
"""

pdf_topic_template = """
You are a knowledgeable and supportive virtual tutor. Rewrite the following educational content to match the learner's level of understanding.

- Learning level: {learning_type}
- Extracted Content: {input_type}

Ensure the rewritten content is engaging, simplified, and helpful for the given learning level.
"""

# Initialize model and prompt
model = OllamaLLM(model="llama3")
manual_prompt = ChatPromptTemplate.from_template(manual_topic_template)
pdf_prompt = ChatPromptTemplate.from_template(pdf_topic_template)

# Pydantic input model
class RewriterInput(BaseModel):
    learning_type: str
    input_type: str = ""  # use 'pdf' for pdf input, else manual text
    pdf_path: str = ""    # local PDF path

# PDF text extraction (first 2 pages)
def extract_text_from_pdf(path: str) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError("PDF file not found.")
    loader = PyPDFLoader(path)
    pages = loader.load()
    return " ".join([page.page_content for page in pages[:2]])

# Output cleaner
def clean_output(text: str) -> str:
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"^\s*[\*\-]\s*", "", text, flags=re.MULTILINE)
    return text.strip()

# Main tutor function
def generate_output(learning_type: str, input_type: str, pdf_path: str = "") -> str:
    if input_type == "pdf":
        topic = extract_text_from_pdf(pdf_path)
        prompt = pdf_prompt
    else:
        topic = input_type
        prompt = manual_prompt

    prompt_input = {
        "learning_type": learning_type,
        "input_type": topic  # <-- this fixes the error
    }

    chain = prompt | model
    result = chain.invoke(prompt_input)
    return clean_output(result)

# FastAPI route
@app.post("/rewriter")
def rewrite_text(data: RewriterInput):
    try:
        output = generate_output(
            learning_type=data.learning_type,
            input_type=data.input_type,
            pdf_path=data.pdf_path
        )
        return {"output": output}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Run app locally with: `python rewriter.py`
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("rewriter:app", host="127.0.0.1", port=5001, reload=True)
