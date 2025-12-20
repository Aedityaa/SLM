import logging
import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

from src.agent.core import MathAgent

load_dotenv()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Math Solver Agent API", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Agent
agent = None

@app.on_event("startup")
async def startup_event():
    global agent
    logger.info("🚀 Initializing Math Agent...")
    try:
        agent = MathAgent()
        logger.info("✅ Math Agent initialized!")
    except Exception as e:
        logger.error(f"❌ Failed to start agent: {e}")

# Simple Request Model (No Files)
class SolveRequest(BaseModel):
    problem: str
    max_tokens: Optional[int] = 2048
    temperature: Optional[float] = 0.7

@app.get("/")
async def root():
    return {"status": "healthy", "service": "Math Solver Agent API"}

@app.post("/solve")
async def solve_problem(request: SolveRequest):
    global agent
    if not agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        logger.info(f"📩 Received input: {request.problem}")
        
        # Run Agent directly with text
        response_text = agent.run(request.problem, max_tokens=request.max_tokens)
        
        return {"response": response_text}

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset")
async def reset_memory():
    global agent
    try:
        agent = MathAgent()
        logger.info("🧹 Agent memory wiped!")
        return {"status": "memory_cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("api.server:app", host="0.0.0.0", port=8000, reload=True)