# Small Language Model (SLM) - Math Problem Solver

An AI-powered math problem solver with intelligent routing, tool-calling capabilities, rich input processing (PDF, OCR, LaTeX, speech), and a modern React frontend. Built with FastAPI + PyTorch transformers, featuring optional LoRA adapters for fine-tuned performance.

---

## 🎯 Features

### Core Capabilities
- **Intelligent Agent System**: Router-based architecture that distinguishes between math problems and general chat using Google Gemini Flash 2.5
- **Multi-format Input Processing**: Supports text, LaTeX, PDF, OCR (images), and speech input via `UniversalMathInputProcessor`
- **Tool-Calling Framework**: Automatic tool selection and execution for complex problem solving with iterative refinement (max 5 iterations)
- **LoRA Fine-tuning Support**: Optional adapter weights for domain-specific improvements (gracefully falls back to base model if not found)
- **Conversation Memory**: Maintains context across multiple interactions using LangChain's `ConversationBufferWindowMemory` (3-turn window)
- **Modern Frontend**: Beautiful React UI with LaTeX rendering (KaTeX), markdown support, and real-time chat interface

### Available Tools
1. **SymPy Solver** (`sympy_solver`): Symbolic mathematics (derivatives, integrals, equation solving, simplification)
2. **NumPy Calculator** (`numpy_calculator`): Numerical computations (trigonometry, arithmetic, exponentials)
3. **Matplotlib Plotter** (`matplotlib_plotter`): Function visualization and graph generation
4. **Code Executor** (`code_executor`): Safe Python code execution sandbox for custom algorithms
5. **Wolfram Alpha** (`wolfram_alpha`): Advanced computations and real-world data (optional, requires API key)

---

## 🏗️ Architecture & Workflow

### System Architecture
```
User Input → Router (Gemini Flash 2.5) → Math Agent → Math Solver Inference → Tools → Response
                ↓
         Conversation Memory (3-turn window)
```

### Processing Pipeline

1. **Input Normalization**: `src/input_processing` processes various input formats:
   - Text cleaning (`text_cleaner.py`) - Unicode normalization, whitespace cleaning
   - LaTeX parsing (`latex_parser.py`) - LaTeX expression extraction
   - OCR processing (`ocr_parser.py`) - Image-to-text conversion for math expressions
   - PDF extraction (`pdf_processor.py`) - PDF text extraction with OCR fallback
   - Speech recognition (`speech_processor.py`) - Speech-to-text conversion
   - Unified formatting (`unified_formatter.py`) - `UniversalMathInputProcessor` coordinates all input types

2. **Intelligent Routing**: `src/input_processing/router.py` uses Google Gemini Flash 2.5 Preview (`gemini-2.5-flash-preview-09-2025`) to:
   - Distinguish math problems from casual chat
   - Refine contextual references (e.g., "solve that" → full problem statement)
   - Route to appropriate handler (math solver or chat response)
   - Returns JSON with `type` ("math" or "chat") and `content` (refined problem)

3. **Math Solving**: `src/agent/core.py` (`MathAgent` class) coordinates:
   - Conversation memory management (3-turn window)
   - Problem routing and refinement via router
   - Solution generation with tool-calling via `MathSolverInference`
   - LaTeX cleaning for frontend display

4. **Model & Inference**: `src/transformer/model.py` and `src/generation/inference.py`:
   - **Base Model**: `Qwen/Qwen2.5-Math-1.5B-Instruct` (loaded via HuggingFace)
   - **LoRA Adapter**: Optional, loaded from `models/lora_adapter/` if present
   - **Device**: Auto-detects CUDA, falls back to CPU
   - **Generation**: `MathGenerator` handles iterative tool-calling (max 5 iterations)
   - **Tool Detection**: Uses regex pattern matching for `<tool_call>` tags in model output
   - **Output Formatting**: LaTeX delimiter cleaning, final answer extraction

5. **Tool Execution**: `src/tools/` provides:
   - **Tool Registry** (`tool_registry.py`): Centralized tool management
   - **Tool Router** (`tool_router.py`): Parses and routes tool calls from model output
   - **Base Tool** (`base_tool.py`): Abstract base class for all tools
   - **Automatic Detection**: Regex-based tool call detection from model output
   - **Result Injection**: Tool results injected back into conversation context
   - **Error Handling**: Graceful error handling with formatted error messages

6. **Output Formatting**: `src/output/formatter.py`:
   - Cleans LaTeX delimiters (`\[`, `\]`, `\(`, `\)` → `$$`, `$`)
   - Extracts final answers (boxed LaTeX or "Final Answer:" patterns)
   - Formats reasoning traces with markdown

---

## 📁 Project Structure

```
SLM/
├── backend/
│   ├── api/
│   │   └── server.py              # FastAPI application and endpoints
│   ├── models/
│   │   └── lora_adapter/          # LoRA adapter weights (optional)
│   │       ├── adapter_config.json
│   │       └── adapter_model.safetensors
│   ├── scripts/
│   │   └── deploy.py              # Deployment helper script
│   ├── src/
│   │   ├── agent/
│   │   │   └── core.py            # MathAgent - main orchestration
│   │   ├── generation/
│   │   │   ├── generator.py       # MathGenerator with tool-calling
│   │   │   ├── inference.py       # MathSolverInference pipeline
│   │   │   └── prompts.py         # Prompt templates (with_tools, step_by_step, etc.)
│   │   ├── input_processing/
│   │   │   ├── __init__.py        # Exports UniversalMathInputProcessor
│   │   │   ├── router.py          # Gemini-based routing logic
│   │   │   ├── latex_parser.py    # LaTeX expression parsing
│   │   │   ├── ocr_parser.py      # OCR for math images
│   │   │   ├── pdf_processor.py   # PDF text extraction
│   │   │   ├── speech_processor.py # Speech-to-text conversion
│   │   │   ├── text_cleaner.py    # Text normalization
│   │   │   └── unified_formatter.py # UniversalMathInputProcessor
│   │   ├── output/
│   │   │   └── formatter.py       # Output formatting and LaTeX cleaning
│   │   ├── tools/
│   │   │   ├── base_tool.py       # Abstract base class for tools
│   │   │   ├── tool_registry.py   # Tool registration system
│   │   │   ├── tool_router.py     # Tool routing and execution logic
│   │   │   ├── sympy_solver.py    # Symbolic math tool
│   │   │   ├── numpy_calculator.py # Numerical computation tool
│   │   │   ├── matplotlib_plotter.py # Visualization tool
│   │   │   ├── code_executor.py   # Python code execution sandbox
│   │   │   └── wolfram_alpha.py   # Wolfram Alpha integration
│   │   └── transformer/
│   │       └── model.py           # Model wrapper with LoRA support
│   ├── requirements.txt           # Python dependencies
│   └── setup.py                   # Package configuration
├── frontend/
│   ├── src/
│   │   ├── App.jsx                # Main React component with chat UI
│   │   ├── main.jsx               # Entry point
│   │   └── index.css              # Styles (currently empty, styles in App.jsx)
│   ├── package.json               # Frontend dependencies
│   ├── vite.config.js             # Vite configuration
│   └── index.html                 # HTML entry point
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- **Python**: 3.10 or higher
- **Node.js**: 18+ (for frontend)
- **System Dependencies** (for PDF/OCR features):
  - Windows: Install [poppler](https://github.com/oschwartz10612/poppler-windows/releases/) and [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)
  - Linux: `apt-get install tesseract-ocr poppler-utils`
  - macOS: `brew install tesseract poppler`
- **GPU** (optional): CUDA-compatible GPU for faster inference
- **API Keys** (required/optional):
  - `GOOGLE_API_KEY`: **Required** for Gemini Flash router functionality
  - `WOLFRAM_API_KEY`: Optional, for Wolfram Alpha integration

### Backend Setup

#### 1. Create Virtual Environment

**Windows:**
```powershell
cd backend
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

#### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 3. Configure Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Required for router functionality
GOOGLE_API_KEY=your_google_api_key_here

# Optional: Wolfram Alpha integration
WOLFRAM_API_KEY=your_wolfram_api_key_here

# Optional: GPU selection
CUDA_VISIBLE_DEVICES=0
```

**Getting API Keys:**
- **Google API Key**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Wolfram Alpha API Key**: Get from [Wolfram Alpha API](https://products.wolframalpha.com/api/)

#### 4. Start the Server

```bash
# Development mode with auto-reload
uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload

# Or use the deployment script
python scripts/deploy.py --mode local --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

**Note**: On first run, the base model (`Qwen/Qwen2.5-Math-1.5B-Instruct`) will be downloaded from HuggingFace (~3GB). This may take several minutes depending on your internet connection.

### Frontend Setup

#### 1. Install Dependencies

```bash
cd frontend
npm install
```

#### 2. Start Development Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

#### 3. Build for Production

```bash
npm run build
npm run preview  # Preview production build
```
---

## 🎨 Frontend Features

- **Modern UI**: Dark theme with gradient accents and animations
- **LaTeX Rendering**: Full support for mathematical notation via KaTeX (`rehype-katex`)
- **Markdown Support**: Rich text formatting with `react-markdown`
- **Real-time Chat**: Smooth scrolling and loading indicators
- **Responsive Design**: Works on desktop and mobile devices
- **Visual Effects**: Animated snowfall (`react-snowfall`) and gradient backgrounds
- **Auto-scroll**: Automatically scrolls to latest message
- **Memory Reset**: Automatically resets backend memory on page load

---
