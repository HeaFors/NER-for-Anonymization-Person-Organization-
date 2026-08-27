from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
# Імпортуємо вашого агента або MCP інструмент
from tesing.agent import process_query # або з mcp_server імпортуйте run_agent_tool

app = FastAPI()

# ОБОВ'ЯЗКОВО: дозволяємо React-сайту робити запити до API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # дозволяє запити з будь-якого фронтенду
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

@app.post("/api/analyze")
async def analyze(request: QueryRequest):
    # Передаємо запит з сайту в агента
    response_text = process_query(request.query)
    return {"response": response_text}