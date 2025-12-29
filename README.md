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

# Optional: Custom LoRA adapter path (defaults to ./models/lora_adapter)
LORA_ADAPTER_PATH=./models/lora_adapter

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

## 🔌 API Endpoints

### Base URL
```
http://localhost:8000
```

### Endpoints

#### `GET /`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "Math Solver Agent API"
}
```

#### `POST /solve`
Solve a single math problem.

**Request Body:**
```json
{
  "problem": "Solve x^2 + 5x + 6 = 0",
  "max_tokens": 2048,
  "temperature": 0.7
}
```

**Parameters:**
- `problem` (string, required): The math problem to solve
- `max_tokens` (integer, optional): Maximum tokens in response (default: 2048)
- `temperature` (float, optional): Sampling temperature (default: 0.7)

**Response:**
```json
{
  "response": "To solve x² + 5x + 6 = 0, we can factor... [solution with LaTeX]"
}
```

**Note**: The API currently accepts text input only. File uploads (PDF, images) are not yet implemented in the API layer, though the processing infrastructure exists.

#### `POST /reset`
Reset the agent's conversation memory.

**Response:**
```json
{
  "status": "memory_cleared"
}
```

**Note**: This endpoint recreates the `MathAgent` instance, effectively clearing all conversation history.

---

## ⚙️ Configuration

### Model Configuration

- **Base Model**: `Qwen/Qwen2.5-Math-1.5B-Instruct` (configurable in `src/generation/inference.py`)
- **LoRA Adapter**: Optional, loaded from `models/lora_adapter/` if present
- **Device**: Auto-detects CUDA, falls back to CPU
- **Model Loading**: Uses `torch.bfloat16` precision, `device_map="auto"` for GPU

### Generation Parameters

- **max_tokens**: Maximum tokens in response (default: 2048, configurable per request)
- **temperature**: Sampling temperature (default: 0.7, configurable per request)
- **max_tool_iterations**: Maximum tool-calling iterations (hardcoded to 5 in `generator.py` to prevent infinite loops)
- **top_p**: Top-p sampling (default: 0.9)
- **top_k**: Top-k sampling (default: 50)
- **repetition_penalty**: Repetition penalty (default: 1.1)

### Memory Configuration

- **Conversation Window**: 3 turns (configurable in `src/agent/core.py`)
- **Memory Type**: `ConversationBufferWindowMemory` from LangChain
- **Memory Format**: String-based history (not message objects)

### Router Configuration

- **Model**: Google Gemini Flash 2.5 Preview (`gemini-2.5-flash-preview-09-2025`)
- **Temperature**: 0 (deterministic routing)
- **Purpose**: Distinguishes math problems from chat, refines contextual references

### Tool Configuration

- **Tool Detection**: Regex pattern matching for `<tool_call>` tags
- **Tool Format**: 
  ```xml
  <tool_call>
  tool: tool_name
  params: {"param1": "value1"}
  </tool_call>
  ```
- **Result Injection**: Tool results injected as `<tool_result>` or `<tool_error>` tags
- **Tool Registry**: Centralized in `tool_registry.py`, tools registered at inference initialization

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

### Frontend Dependencies

- **React 19**: Latest React with hooks
- **Vite 7**: Fast build tool and dev server
- **KaTeX**: LaTeX rendering (`katex`, `rehype-katex`, `remark-math`)
- **React Markdown**: Markdown parsing (`react-markdown`)
- **Lucide React**: Icon library
- **React Snowfall**: Visual effects

---

## 📝 Important Notes

### Environment Variables

- **`GOOGLE_API_KEY`**: **Required** for router functionality. Without it, the agent cannot distinguish between math problems and chat.
- **`WOLFRAM_API_KEY`**: Optional, enables Wolfram Alpha tool for advanced computations. Pass `enable_wolfram=True` when initializing `MathAgent` or `MathSolverInference`.
- **`LORA_ADAPTER_PATH`**: Optional, defaults to `./models/lora_adapter`. System works without LoRA adapter.

### Model Loading

- First run downloads the base model (~3GB) from HuggingFace
- LoRA adapter is optional - system gracefully falls back to base model if not found
- GPU recommended for faster inference, but CPU works fine
- Model uses `bfloat16` precision for memory efficiency

### Tool-Calling

- Tools are automatically detected from model output using regex patterns
- Maximum iterations (5) prevent infinite loops
- Code execution runs in a sandboxed environment (via `code_executor.py`)
- Tool results are injected back into the conversation context
- Tool calls are parsed from `<tool_call>` XML-like tags

### Input Processing

- **Current API Limitation**: The API currently only accepts text input via JSON. File uploads (PDF, images, audio) are not yet implemented in the API endpoints, though the processing infrastructure (`UniversalMathInputProcessor`) exists.
- PDF processing requires `poppler-utils`
- OCR requires `tesseract-ocr`
- Speech processing requires microphone access (not yet integrated in API)
- All inputs are normalized to unified format before processing

### Router Behavior

- Uses Google Gemini Flash 2.5 Preview for fast, cost-effective routing
- Returns JSON with `type` ("math" or "chat") and `content` (refined problem)
- Handles contextual references (e.g., "solve that" → full problem statement)
- Falls back to math routing if JSON parsing fails

### Performance Tips

1. **GPU Acceleration**: Use CUDA-enabled GPU for 5-10x faster inference
2. **Model Quantization**: Consider quantizing the model for faster CPU inference
3. **Caching**: Conversation memory reduces redundant computations
4. **Batch Processing**: Currently not implemented, but could be added for multiple problems

### Production Recommendations

1. **Security**:
   - Add authentication/authorization
   - Implement rate limiting
   - Validate and sanitize inputs
   - Secure API keys (use secrets management)
   - Add input validation for tool parameters

2. **Monitoring**:
   - Add logging and metrics
   - Monitor API response times
   - Track tool usage statistics
   - Set up error alerting
   - Log tool execution results

3. **Scalability**:
   - Use model serving frameworks (vLLM, TensorRT)
   - Implement request queuing
   - Add load balancing
   - Consider model sharding
   - Add connection pooling for database (if added)

4. **Cost Optimization**:
   - Cache common queries
   - Use model quantization
   - Implement request batching
   - Monitor API usage (Google/Wolfram)
   - Consider using smaller models for routing

---

## 🔧 Troubleshooting

### Common Issues

**Issue**: `python3.10` not found (Windows)
- **Solution**: Use `python` instead of `python3.10` on Windows

**Issue**: Model download fails
- **Solution**: Check internet connection, ensure HuggingFace access, or manually download model

**Issue**: CUDA out of memory
- **Solution**: Reduce batch size, use CPU, or enable model quantization

**Issue**: Router returns errors
- **Solution**: Verify `GOOGLE_API_KEY` is set correctly in `.env` file

**Issue**: LoRA adapter not loading
- **Solution**: Check path in `LORA_ADAPTER_PATH`, verify files exist. System will use base model if not found (this is expected behavior).

**Issue**: Frontend cannot connect to backend
- **Solution**: Ensure backend is running on port 8000, check CORS settings (already enabled), verify API URL in frontend (`http://localhost:8000`)

**Issue**: Tool calls not being detected
- **Solution**: Check that model output contains `<tool_call>` tags. Verify tool registry has tools registered. Check `max_tool_iterations` hasn't been exceeded.

**Issue**: Hardcoded Windows path in `inference.py`
- **Solution**: The `lora_adapter_path` parameter in `MathSolverInference.__init__` has a hardcoded Windows path. Use environment variable `LORA_ADAPTER_PATH` or relative path `./models/lora_adapter` instead.

---

## 📚 Dependencies

### Backend Key Dependencies
- `torch>=2.4.0`: PyTorch for model inference
- `transformers>=4.45.0`: HuggingFace transformers
- `peft>=0.18.0`: Parameter-Efficient Fine-Tuning (LoRA)
- `fastapi==0.104.1`: Web framework
- `uvicorn==0.24.0`: ASGI server
- `langchain>=0.1.0`: Agent framework and memory
- `langchain-google-genai>=0.0.3`: Google Gemini integration
- `sympy==1.12`: Symbolic mathematics
- `numpy==1.26.2`: Numerical computations
- `matplotlib==3.8.2`: Plotting and visualization
- `pytesseract==0.3.10`: OCR functionality
- `PyPDF2==3.0.1`: PDF processing
- `pdf2image==1.16.3`: PDF to image conversion
- `SpeechRecognition==3.10.0`: Speech-to-text
- `python-dotenv==1.0.0`: Environment variable management
- `pydantic==2.5.2`: Data validation
- `requests==2.31.0`: HTTP library (for Wolfram Alpha)

### Frontend Key Dependencies
- `react^19.2.0`: UI framework
- `vite^7.2.4`: Build tool
- `katex^0.16.27`: LaTeX rendering
- `react-markdown^10.1.0`: Markdown parsing
- `rehype-katex^7.0.1`: KaTeX plugin for markdown
- `remark-math^6.0.0`: Math plugin for markdown
- `lucide-react^0.562.0`: Icons
- `react-snowfall^2.4.0`: Visual effects

---

## 👥 Contributors

- **Aditya Parate**
- **Prakhar Gupta**
- **Ansh Agarwal**

---

## 📄 License

[Add your license information here]

---

## 🙏 Acknowledgments

- **Qwen Team**: For the excellent Qwen2.5-Math model
- **HuggingFace**: For transformers and PEFT libraries
- **LangChain**: For agent framework and memory management
- **Google**: For Gemini Flash API

---

## 🔮 Future Enhancements

- [ ] Multi-modal input (images, diagrams) via API endpoints
- [ ] Step-by-step solution visualization
- [ ] Export solutions as PDF/LaTeX
- [ ] Collaborative problem solving
- [ ] Custom tool creation interface
- [ ] Model fine-tuning pipeline
- [ ] Advanced caching and optimization
- [ ] Mobile app support
- [ ] Batch processing endpoint
- [ ] File upload endpoints (PDF, images, audio)
- [ ] Tool usage analytics and monitoring
- [ ] Model quantization support
- [ ] Docker deployment configuration

---

## 📞 Support

For issues, questions, or contributions, please open an issue on the repository.
