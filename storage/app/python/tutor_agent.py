# storage/app/python/tutor_agent.py

import os
import re
from pydantic import BaseModel, ValidationError
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from fastapi import UploadFile
import tempfile, os, re

# Define your prompt templates
manual_topic_template = """
You are an experienced and friendly virtual tutor...

- Grade Level: {grade_level}
- Topic: {topic}
- Additional Context or Learning Needs: {add_cont}
...
"""

pdf_topic_template = """
You are a knowledgeable and supportive virtual tutor...

- Grade Level: {grade_level}
- Extracted Content: {topic}
- Additional Notes: {add_cont}
...
"""

# Initialize your language model and prompt templates
model = OllamaLLM(model="gemma3")
manual_prompt = ChatPromptTemplate.from_template(manual_topic_template)
pdf_prompt = ChatPromptTemplate.from_template(pdf_topic_template)

# Pydantic model used for input validation
class TutorInput(BaseModel):
    grade_level: str
    input_type: str
    topic: str = ""
    pdf_path: str = ""
    add_cont: str = ""

# Function to extract text from PDF (using only the first 2 pages)
def extract_text_from_pdf(path: str) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError("PDF file not found.")
    loader = PyPDFLoader(path)
    pages = loader.load()
    return " ".join([page.page_content for page in pages[:2]])

# Function to clean the output from formatting artifacts
def clean_output(text: str) -> str:
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"^\s*[\*\-]\s*", "", text, flags=re.MULTILINE)
    return text.strip()

# Main function containing the tutor logic
async def generate_output_with_file(grade_level, input_type, topic="", add_cont="", pdf_file: UploadFile = None):
    if input_type == "pdf":
        # Save PDF temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await pdf_file.read()
            tmp.write(content)
            tmp_path = tmp.name

        topic = extract_text_from_pdf(tmp_path)
        os.unlink(tmp_path)  # Delete file after use
        prompt = pdf_prompt
    else:
        prompt = manual_prompt

    user_input = {
        "grade_level": grade_level,
        "input_type": input_type,
        "topic": topic,
        "pdf_path": "",
        "add_cont": add_cont
    }

    chain = prompt | model
    result = chain.invoke(user_input)
    return clean_output(result)
