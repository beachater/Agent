from langchain_community.llms import Ollama  # type: ignore
from langchain_core.prompts import ChatPromptTemplate   # type: ignore  
from langchain_community.document_loaders.pdf import PyPDFLoader  # type: ignore

# Prompt template for adaptive content only
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

def get_adaptive_content(context: str, grade_level: str, learning_speed: str):
    response = chain.invoke({
        "context": context,
        "grade_level": grade_level,
        "learning_speed": learning_speed
    })
    # The response content is the adapted explanation string
    print("\nAdapted Explanation:")
    print(response)

def load_pdf_content(pdf_path: str) -> str:
    loader = PyPDFLoader(pdf_path)
    # This returns a list of Document objects, each with .page_content
    documents = loader.load()
    # Join the text from all pages into one big string
    full_text = "\n".join(doc.page_content for doc in documents)
    return full_text

if __name__ == "__main__":
    print("Adaptive Content Chatbot (type 'exit' to quit)\n")

    while True:
        user_input = input("Enter a sentence, topic, or type 'pdf' to load content from a PDF: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        if user_input.lower() == "pdf":
            pdf_path = input("Enter the path to the PDF file: ").strip()
            try:
                pdf_text = load_pdf_content(pdf_path)
                print(f"Loaded PDF content ({len(pdf_text)} characters).")
                context = pdf_text
            except Exception as e:
                print(f"Failed to load PDF: {e}")
                continue
        else:
            context = user_input

        grade_level = input("Enter grade level (kinder, elementary, middle, high, college): ").strip().lower()
        learning_speed = input("Enter learning speed (slow, average, fast): ").strip().lower()

        get_adaptive_content(context, grade_level, learning_speed)