from pydantic import BaseModel, Field, ValidationError
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader
import os
import re

# -------------------------------
# Pydantic Model
# -------------------------------
class TutorInput(BaseModel):
    grade_level: str = Field(..., description="Student's grade level (e.g., '11th grade')")
    input_type: str = Field(..., pattern="^(topic|pdf)$", description="Input type: 'topic' or 'pdf'")
    topic: str = Field(default="", description="Topic for explanation (used if input_type is 'topic')")
    pdf_path: str = Field(default="", description="Path to PDF file (used if input_type is 'pdf')")
    add_cont: str = Field(default="", description="Additional context, if any")

# -------------------------------
# Prompt Templates
# -------------------------------
manual_topic_template = """
You are an experienced and friendly virtual tutor. Your goal is to help the student understand the concept clearly and effectively based on the following details:

- Grade Level: {grade_level}
- Topic: {topic}
- Additional Context or Learning Needs: {add_cont}

Please follow these guidelines in your response:
1. Start with a simple, high-level explanation appropriate for the student's grade level.
2. Break down the concept into smaller parts if needed.
3. Use real-world examples or analogies to make it easier to understand.
4. Avoid technical jargon unless appropriate, and explain it if used.
5. End with a conceptual summary reinforce understanding.
"""

pdf_topic_template = """
You are a knowledgeable and supportive virtual tutor. A student has provided some content from their study material and wants a clear explanation of it.

- Grade Level: {grade_level}
- Extracted Content: {topic}
- Additional Notes: {add_cont}

Your task is to explain the topic in a way that suits the student's level, using simple language, examples, and optionally ending with a summary or a guiding question.
"""

# -------------------------------
# LangChain Setup
# -------------------------------
model = OllamaLLM(model="gemma3")

manual_prompt = ChatPromptTemplate.from_template(manual_topic_template)
pdf_prompt = ChatPromptTemplate.from_template(pdf_topic_template)

# -------------------------------
# Load PDF Content
# -------------------------------
def extract_text_from_pdf(path: str) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError("PDF file not found.")
    loader = PyPDFLoader(path)
    pages = loader.load()
    return " ".join([page.page_content for page in pages[:2]])  # Limit to first 2 pages

def clean_output(text: str) -> str:
    # Remove bold and italic markers (e.g., **text**, *text*)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    # Remove leading bullet points and extra whitespace
    text = re.sub(r"^\s*[\*\-]\s*", "", text, flags=re.MULTILINE)
    return text.strip()



# -------------------------------
# Main Interactive Loop
# -------------------------------

def main():
    try:
        grade_level = input("Enter grade level (e.g., '11th grade'): ").strip()
        input_type = input("Type 'topic' to manually enter a topic or 'pdf' to use a PDF: ").strip().lower()

        topic = ""
        pdf_path = ""

        if input_type == "topic":
            topic = input("Enter the topic to be explained: ").strip()
        elif input_type == "pdf":
            pdf_path = input("Enter full path to the PDF: ").strip()
            topic = extract_text_from_pdf(pdf_path)
        else:
            raise ValueError("Invalid input type. Please enter 'topic' or 'pdf'.")

        add_cont = input("Any additional context (optional): ").strip()

        # Validate input with Pydantic
        user_input = TutorInput(
            grade_level=grade_level,
            input_type=input_type,
            topic=topic,
            pdf_path=pdf_path,
            add_cont=add_cont
        )

        # Choose the appropriate chain
        if input_type == "pdf":
            chain = pdf_prompt | model
        else:
            chain = manual_prompt | model

        result = chain.invoke(user_input.model_dump())
        print("\n--- Tutor's Explanation ---")
        print(clean_output(result))

    except ValidationError as e:
        print("Input validation failed:")
        print(e)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
