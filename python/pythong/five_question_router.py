# five_question_router.py
from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import JSONResponse
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
import mysql.connector
import traceback
import re
from typing import List

five_question_router = APIRouter()

# ====================== LangChain Setup ======================

chat_prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI that continues a conversation about generating thoughtful, open-ended questions to promote critical thinking. Based on the previous conversation and the student's grade level and the main topic, provide the next set of five unique, deep, and age-appropriate questions or respond to the user's inquiry within the context of generating questions. Keep responses clear and concise."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "Grade Level: {grade_level}\nTopic: {topic}\nCurrent message: {current_message}")
])

model = Ollama(model="gemma3:1b")
chat_chain: Runnable = chat_prompt_template | model

# ====================== DB Message History ======================

class DBChatHistory(BaseChatMessageHistory):
    def __init__(self, user_id: int, message_id: int, agent_name: str):
        self.user_id = user_id
        self.agent_name = agent_name
        self.message_id = message_id
        self._load()

    def _connect(self):
        return mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            port=3306,
            password="",
            database="ck_agent" # Ensure this database exists
        )

    def _get_agent_id(self, cursor):
        cursor.execute("SELECT id FROM agents WHERE agent = %s", (self.agent_name,)) # Use 'agent' column
        agent_id_row = cursor.fetchone()
        if not agent_id_row:
            raise ValueError(f"Agent '{self.agent_name}' not found in 'agents' table.")
        return agent_id_row[0]

    def _load(self):
        self._messages: list[BaseMessage] = []
        conn = self._connect()
        cursor = conn.cursor(dictionary=True)
        try:
            agent_id = self._get_agent_id(cursor)
            cursor.execute("""
                SELECT sender, topic FROM messages
                WHERE user_id = %s AND message_id = %s AND agent_id = %s
                ORDER BY created_at
            """, (self.user_id, self.message_id, agent_id))
            for row in cursor.fetchall():
                if row["sender"] == "human":
                    self._messages.append(HumanMessage(content=row["topic"]))
                elif row["sender"] == "ai":
                    self._messages.append(AIMessage(content=row["topic"]))
        except Exception as e:
            print(f"Error loading messages from DB: {e}")
        finally:
            cursor.close()
            conn.close()

    @property
    def messages(self) -> list[BaseMessage]:
        return self._messages

    def add_user_message(self, message: str) -> None:
        self._messages.append(HumanMessage(content=message))
        self._save_message(message, "human")

    def add_ai_message(self, message: str) -> None:
        self._messages.append(AIMessage(content=message))
        self._save_message(message, "ai")

    def _save_message(self, message: str, sender: str) -> None:
        conn = self._connect()
        cursor = conn.cursor()
        try:
            agent_id = self._get_agent_id(cursor)
            # IMPORTANT: parameter_inputs_id is hardcoded to 1.
            # Ensure your 'parameter_inputs' table exists and has an ID of 1,
            # or modify your DB schema to make 'parameter_inputs' nullable
            # if it's not always relevant for chat messages.
            parameter_inputs_id = 1 # Placeholder, adjust as per your DB logic

            cursor.execute("""
                INSERT INTO messages (agent_id, user_id, parameter_inputs, sender, message_id, topic, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
            """, (
                agent_id,
                self.user_id,
                parameter_inputs_id, # Value for parameter_inputs
                sender,
                self.message_id,
                message
            ))
            conn.commit()
        except Exception as e:
            print(f"Error saving message to DB: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

    def clear(self) -> None:
        conn = self._connect()
        cursor = conn.cursor()
        try:
            agent_id = self._get_agent_id(cursor)
            cursor.execute("""
                DELETE FROM messages
                WHERE user_id = %s AND message_id = %s AND agent_id = %s
            """, (self.user_id, self.message_id, agent_id))
            conn.commit()
        except Exception as e:
            print(f"Error clearing messages from DB: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
        self._messages = []

# ====================== Runnable With DB-Backed History ======================

def get_history(session_id: str) -> BaseChatMessageHistory:
    print(f"[DEBUG] five_question_router: raw session_id: {session_id}")
    # session_id should be "user_id:message_id"
    user_id_str, message_id_str = session_id.split(":")
    user_id = int(user_id_str)
    message_id = int(message_id_str)
    return DBChatHistory(user_id=user_id, message_id=message_id, agent_name="five-question") # Agent name from seeder

chat_with_memory = RunnableWithMessageHistory(
    chat_chain,
    get_session_history=get_history,
    input_messages_key="current_message",
    history_messages_key="history"
)

# ====================== Helper for Questions ======================
def extract_questions(raw: str) -> List[str]:
    pattern = r"\b\d\.\s+(.*?)(?=\n\d\.|\Z)"
    questions = re.findall(pattern, raw, flags=re.DOTALL)
    return [q.strip() for q in questions][:5]

# ====================== Endpoint ======================
@five_question_router.post("/fiveq_chat")
async def five_question_chat_api(
    grade_level: str = Form(...),
    prompt: str = Form(...), # This is the original topic for context
    current_message: str = Form(...), # This is the user's latest message in the chat
    db_message_id: int = Form(...),
    user_id: int = Form(...)
):
    try:
        print(f"[DEBUG] fiveq_chat request: user_id={user_id}, db_message_id={db_message_id}, grade_level={grade_level}, prompt={prompt}, current_message={current_message}")

        session_key = f"{user_id}:{db_message_id}"

        result = await chat_with_memory.ainvoke(
            {
                "grade_level": grade_level,
                "topic": prompt, # The original topic for context
                "current_message": current_message # The actual user input for this turn
            },
            config={
                "configurable": {
                    "session_id": session_key
                }
            }
        )

        extracted_questions = extract_questions(result)
        if extracted_questions and len(extracted_questions) == 5: # Only return questions if exactly 5 were found
            return JSONResponse(content={"questions": extracted_questions})
        else:
            return JSONResponse(content={"response": result}) # Otherwise, return the raw chat response

    except Exception as e:
        traceback_str = traceback.format_exc()
        print(f"[Five Question Chat Error] {e}\n{traceback_str}")
        raise HTTPException(status_code=500, detail=f"Five question chat processing failed: {e}")