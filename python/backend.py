from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from conceptual_understanding import TutorInput, extract_text_from_pdf, clean_output, manual_prompt, pdf_prompt, model

app = FastAPI()

# Allow CORS so frontend can call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for production, restrict to frontend origin
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/tutor")
async def tutor_api(request: Request):
    try:
        data = await request.json()

        if data["input_type"] == "pdf":
            data["topic"] = extract_text_from_pdf(data["pdf_path"])

        user_input = TutorInput(**data)

        chain = pdf_prompt | model if data["input_type"] == "pdf" else manual_prompt | model
        result = chain.invoke(user_input.model_dump())

        return {"output": clean_output(result)}

    except ValidationError as ve:
        return {"error": ve.errors()}
    except Exception as e:
        return {"error": str(e)}
