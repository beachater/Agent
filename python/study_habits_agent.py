# study_habits_agent.py
from pydantic import BaseModel
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

class StudyPlanInput(BaseModel):
    grade_level: str
    goal: str

# Optional grade profiles for age-based tone/style
GRADE_PROFILES = {
    "kindergarten": "Use playful, simple words. Focus on routines, fun learning moments, and positive reinforcement. Keep sessions short and colorful.",
    "elementary": "Use friendly and fun language. Break tasks into small steps. Focus on creating habits, using visual aids, and celebrating effort.",
    "junior high": "Use engaging and relatable tone. Encourage organization, self-motivation, and balancing school and personal life.",
    "senior high": "Use mature, focused advice. Address time management, review techniques, and subject-specific strategies.",
    "college": "Use academic tone. Focus on deep learning, exam strategy, scheduling, and productivity systems like Pomodoro or spaced repetition."
}

def generate_study_plan(grade_level: str, goal: str) -> str:
    profile = GRADE_PROFILES.get(grade_level.lower(), "Use clear, student-friendly language appropriate for the grade level.")

    prompt = f"""
You are a smart AI tutor.

Your task is to generate a practical, organized, and motivational study plan for a student in grade level "{grade_level}".
The student's preparation goal is:
"{goal}"

Student Profile: {profile}

Instructions:
- Use plain formatting (no asterisks or markdown bold) to make it clean and readable.
- Structure the plan by weeks (e.g., Week 1: Title).
- Each week should include 5 study days and 1 rest day.
- Use simple formatting like:
  Day 1 - Topic (duration)
    Activity: ...
    Review: ...
    Tool: ...
- End with an encouraging note.
- Avoid using excessive symbols like *** or ###.
- No headings like "Final Note" — just a natural closing message.

Keep it visually simple but still structured.
"""

    model = OllamaLLM(model="gemma3")
    chain = ChatPromptTemplate.from_template(prompt) | model
    result = chain.invoke({})
    return result.strip()
