from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
from agent import ask_agent

app = FastAPI()

class QuestionRequest(BaseModel):
    question: str

@app.post("/ask/")
async def ask(request: QuestionRequest):
    response = ask_agent(request.question)
    return response