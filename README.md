# Small Language Model (SLM)

AI-powered math problem solver with tool-calling, rich input processing (PDF, OCR, LaTeX, speech), and a React frontend scaffold. Backend is FastAPI + PyTorch transformers with optional LoRA adapters; frontend is Vite/React ready for UI integration.

---

## Approach & Workflow
- **Input normalization:** `src/input_processing` cleans text (`text_cleaner.py`), parses LaTeX/MathOCR/PDF (`latex_parser.py`, `ocr_parser.py`, `pdf_processor.py`), and unifies formats via `unified_formatter.py`. Speech input hooks are available in `speech_processor.py`.
- **Prompting:** `src/generation/prompts.py` builds chat-style prompts for the solver with or without tools.
- **Model + LoRA:** `src/transformer/model.py` loads the base model (default `Qwen/Qwen2.5-Math-1.5B-Instruct`) and optionally merges a LoRA adapter from `models/lora_adapter`.
- **Generation loop:** `MathGenerator` (`src/generation/generator.py`) iteratively generates responses, detects tool-calls, executes tools, and injects results back into the conversation (guarded by `max_tool_iterations` to avoid loops).
- **Tooling layer:** `src/tools` registers numeric (`numpy_calculator`), symbolic (`sympy_solver`), plotting (`matplotlib_plotter`), code execution sandbox, and external utilities (`wolfram_alpha`). Routing/registry in `tool_router.py` and `tool_registry.py`.
- **Output shaping:** `src/output/formatter.py` formats reasoning traces and extracts final answers for API responses.
- **Serving:** FastAPI service in `backend/api/server.py` exposes health, solve (single/batch), and tool-list endpoints with CORS enabled for the frontend.

---

## Project Structure
```
backend/
  api/server.py           # FastAPI app and endpoints
  docker/                 # Dockerfile + compose (GPU optional)
  scripts/                # Deploy/test helpers
  src/
    generation/           # Prompting, generation, LoRA-aware inference
    input_processing/     # PDF/OCR/LaTeX/speech/text normalization
    output/               # Formatting and final-answer extraction
    tools/                # Tool registry/router + numeric/symbolic/exec
    transformer/          # Model wrapper and adapter loading
frontend/
  src/                    # Vite + React scaffold (ready for UI wiring)
  package.json            # npm scripts (dev/build/lint/preview)
```

---

## Backend: Running Locally
Prerequisites: Python 3.10+, optionally CUDA/GPU; system deps for PDF/OCR if using those paths (poppler, tesseract).

```bash
cd backend
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload
```

Environment flags:
- `LORA_ADAPTER_PATH` (optional): path to adapter weights; defaults to `./models/lora_adapter`.
- `CUDA_VISIBLE_DEVICES`: select GPU; unset to force CPU.

API surface:
- `GET /` or `/health` – service status and loaded tools.
- `GET /tools` – available tool registry.
- `POST /solve` – solve a single problem (`problem`, `system_prompt`, `max_tokens`, `temperature`, `use_tools`).
- `POST /solve-batch` – submit multiple problems.

Testing helpers:
- `python scripts/test_api.py` – quick request/response check.
- `python scripts/deploy.py` – deployment helper scaffold.

---

## Backend: Docker / Compose
With Docker (CPU):
```bash
cd backend
docker build -f docker/Dockerfile -t slm-backend .
docker run -p 8000:8000 slm-backend
```

With Docker Compose + GPU:
```bash
cd backend/docker
docker compose up --build
```
Mounts `../models` and `../data` into the container; ensures `LORA_ADAPTER_PATH=/app/models/lora_adapter`.

---

## Frontend (Vite + React)
Currently a starter UI scaffold; ready to connect to the FastAPI endpoints.

```bash
cd frontend
npm install
npm run dev      # starts Vite dev server (default http://localhost:5173)
npm run build    # production build
npm run preview  # serve built assets locally
```

To integrate with the backend:
- Call `POST http://localhost:8000/solve` from React (consider CORS already enabled).
- Render reasoning trace, tool calls, and final answers from the API response.
- Add input modes (text, PDF upload, speech) aligned with backend processors.

---

## Typical Solve Flow (end-to-end)
1) User submits math problem (text/PDF/LaTeX/speech).  
2) Input processors clean/normalize to a unified representation.  
3) Prompt builder packages conversation context (`with_tools` by default).  
4) Generator runs; detects/executes tools iteratively (numeric, symbolic, plotting, code exec, Wolfram Alpha) with loop guard.  
5) Output formatter returns structured solution, formatted reasoning, final answer, and tool-call trace.  
6) Frontend renders solution; batch mode available for multiple problems.  

---

## Notes & Recommendations
- Place models/LoRA weights under `models/` (mapped in compose) to avoid large downloads at runtime.
- PDF/OCR flows require `poppler-utils` and `tesseract-ocr` (already installed in the Docker image).
- Keep `max_tokens` and `temperature` balanced for correctness; tool-calling can be toggled per request.
- For production, pin GPU image, add auth/rate limiting, and persist logs/metrics.

---

## Contributors
- Aditya Parate
- Prakhar Gupta
- Ansh Agarwal
