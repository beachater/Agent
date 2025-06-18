from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.document_loaders import PyPDFLoader
import os

# Step 1: Choose input type
input_type = input("Input type? ('text' or 'pdf'): ").strip().lower()

if input_type == "pdf":
    pdf_path = input("📎 Enter path to PDF file: ").strip().strip('"')
    if not os.path.isfile(pdf_path):
        print("File not found. Please check the path.")
        exit()
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    text = "\n".join([page.page_content for page in pages])
else:
    text = input("Paste your text to summarize:\n\n").strip()

# Step 2: Set initial summary conditions
conditions = input("Enter summary conditions (e.g., 1 paragraph, 5 bullet points, 300 words): ").strip()

# Step 3: Define reusable prompt template
template = """
You are an intelligent and concise summarization assistant.

Your task is to read the content below and generate a summary that follows the user's specific request.

------------------------
Content:
{text}

Summary Instructions:
{conditions}
------------------------

Please follow the instructions carefully and provide only the summary.
"""
prompt = PromptTemplate.from_template(template)
llm = Ollama(model="gemma3:4b")
# Chain using RunnableSequence (no LLMChain)
chain = prompt | llm

# Then run using `.invoke()` with your inputs
response = chain.invoke({"text": text, "conditions": conditions})


# Step 4: Summary loop
while True:
    # Run the summary
    response = chain.run(text=text, conditions=conditions)
    print("\nSummary:\n")
    print(response.strip())

    # Ask user if they want to run again
    next_action = input(
        "\nWould you like to summarize again with updated conditions? (add / replace / keep / exit): "
    ).strip().lower()

    if next_action == "add":
        extra = input("Enter additional condition(s) to add: ").strip()
        conditions = conditions + "; " + extra
    elif next_action == "replace":
        conditions = input("Enter new condition(s) to replace the old ones: ").strip()
    elif next_action == "keep":
        print("Reusing existing conditions.")
        continue
    elif next_action == "exit":
        print("Exiting. Thank you!")
        break
    else:
        print("Invalid option. Please type 'add', 'replace', 'keep', or 'exit'.")
