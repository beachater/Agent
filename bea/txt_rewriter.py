from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
from langchain_community.document_loaders.pdf import PyPDFLoader
import os

# Use the updated OllamaLLM class
llm = OllamaLLM(model="llama3")

prompt = PromptTemplate.from_template(
    "You are an assistant who rewrites content to suit different types of learners.\n\n"
    "Learner Type: {learner_type}\n"
    "Task: Rewrite the following input text so that it is easier to understand for this learner type.\n\n"
    "Input Text:\n{input_text}\n\n"
    "Output only the rewritten version without any explanation or comments."
)

chain = prompt | llm

print("Text Rewriter\nType 'exit' to quit.\n")

while True:
    mode = input("Enter 'text' to input manually or 'pdf' to load from a PDF: ").lower()
    
    if mode == "exit":
        break

    elif mode == "text":
        text = input("Text: ")
        if text.lower() == "exit":
            break

    elif mode == "pdf":
        file_path = input("Enter PDF file path: ").strip()
        if not os.path.exists(file_path):
            print("File not found.\n")
            continue
        try:
            loader = PyPDFLoader(file_path)
            pages = loader.load()
            text = "\n".join([page.page_content for page in pages])
            print(f"\nPDF loaded successfully. {len(pages)} pages extracted.\n")
        except Exception as e:
            print(f"Failed to load PDF: {e}")
            continue

    else:
        print("Invalid option. Type 'text', 'pdf', or 'exit'.\n")
        continue

    level = input("Level (slow/average/fast): ").lower()
    if level not in ["slow", "average", "fast"]:
        print("Invalid level\n")
        continue

    learner = f"{level} learner"
    result = chain.invoke({"learner_type": learner, "input_text": text})
    print("\nRewritten:\n" + result + "\n")
