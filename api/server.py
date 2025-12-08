"""FastAPI server with tool support"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
from dotenv import load_dotenv

from src.generation.inference import MathSolverInference

load_dotenv()

app = FastAPI(
    title="Math Solver API with Tools",
    description="AI-powered mathematical problem solver with tool calling support",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LORA_PATH = os.getenv("LORA_ADAPTER_PATH", "./models/lora_adapter")
solver = None

@app.on_event("startup")
async def startup_event():
    global solver
    print("🚀 Starting Math Solver API with Tools...")
    solver = MathSolverInference(
        lora_adapter_path=LORA_PATH if os.path.exists(LORA_PATH) else None,
        enable_tools=True
    )
    print("✅ API Ready with Tools!")

class SolveRequest(BaseModel):
    problem: str
    system_prompt: str = "with_tools"
    max_tokens: int = 512
    temperature: float = 0.7
    use_tools: bool = True

class SolveResponse(BaseModel):
    problem: str
    solution: str
    formatted: str
    final_answer: Optional[str]
    tool_calls: List[Dict]
    tools_used: bool

@app.get("/")
async def root():
    return {
        "status": "healthy",
        "service": "Math Solver API with Tools",
        "version": "2.0.0",
        "tools_enabled": True
    }

@app.post("/solve", response_model=SolveResponse)
async def solve_problem(request: SolveRequest):
    """Solve a math problem with optional tool calling"""
    try:
        result = solver.solve(
            problem=request.problem,
            system_prompt=request.system_prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            use_tools=request.use_tools
        )
        return SolveResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools")
async def list_tools():
    """List all available tools"""
    return {
        "tools": solver.get_available_tools()
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": solver is not None,
        "lora_loaded": os.path.exists(LORA_PATH),
        "tools_enabled": True,
        "available_tools": list(solver.get_available_tools().keys()) if solver else []
    }