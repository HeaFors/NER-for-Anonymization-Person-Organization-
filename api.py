from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from tesing.agent import process_query

app = FastAPI(title="NER & RAG AI Analyst API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: str
    success: bool = True
    error: Optional[str] = None

@app.post("/api/analyze", response_model=QueryResponse)
async def analyze(request: QueryRequest):
    try:
        response_text = process_query(request.query)
        return QueryResponse(
            response=response_text,
            success=True
        )
    except Exception as e:
        return QueryResponse(
            response="Помилка під час обробки запиту.",
            success=False,
            error=str(e)
        )