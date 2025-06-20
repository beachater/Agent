import os
import re
from pydantic import BaseModel, ValidationError
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader
import uvicorn

# Define your prompt templates
manual_topic_template = """
You are an experienced and friendly virtual tutor...

- Learner Type: {learner_type}
- Topic: {topic}
- Additional Context or Learning Needs: {add_cont}
...
"""

pdf_topic_template = """
You are a knowledgeable and supportive virtual tutor...

- Learner Type: {learner_type}
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
    learner_type: str  # Replaced 'grade_level' with 'learner_type'
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
def generate_output(learner_type: str, input_type: str, topic: str = "", pdf_path: str = "", add_cont: str = "") -> str:
    if input_type == "pdf":
        topic = extract_text_from_pdf(pdf_path)
        prompt = pdf_prompt
    else:
        prompt = manual_prompt

    # Validate and prepare user input
    user_input = TutorInput(
        learner_type=learner_type,  # Pass learner_type instead of grade_level
        input_type=input_type,
        topic=topic,
        pdf_path=pdf_path,
        add_cont=add_cont
    )

    # Create a chain: prompt template piped to your model
    chain = prompt | model
    result = chain.invoke(user_input.model_dump())
    return clean_output(result)

if __name__ == "__main__":
    uvicorn.run("rewriter:app", host="127.0.0.1", port=5001, reload=True)