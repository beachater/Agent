from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# Prompt template for proofreading
Template = """
You are a professional proofreader. Proofread the following text and:
1. Correct grammar errors
2. Fix spelling mistakes
3. Adjust punctuation
4. Improve clarity while preserving the meaning
5. Return the corrected version and a list of changes

Text:
{input_text}

Respond in this format:
Corrected text:
[Your corrected version]

Changes made:
[List of major changes]
"""

# Load model from Ollama
model = OllamaLLM(model="llama3.1")  
prompt = ChatPromptTemplate.from_template(Template)
chain = prompt | model

# App loop
def run_proofreader():
    print("=== Local LLM Proofreader ===")
    print("Enter text to proofread. Type 'exit' to quit.\n")

    while True:
        user_input = input("Text to proofread: ")

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        if not user_input.strip():
            print("Please enter valid text.")
            continue

        try:
            result = chain.invoke({"input_text": user_input})
            print("\n=== Proofreading Result ===")
            print(result)
            print("===========================\n")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    run_proofreader()
