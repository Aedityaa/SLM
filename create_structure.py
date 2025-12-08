import os

structure = {
    "config": ["__init__.py", "model_config.yaml", "tool_config.yaml", "deployment_config.yaml"],
    "src": {
        "__init__.py": None,
        "input_processing": ["__init__.py", "ocr_parser.py", "latex_parser.py", "text_cleaner.py", "unified_formatter.py"],
        "tokenization": {
            "__init__.py": None,
            "math_tokenizer.py": None,
            "special_tokens.py": None,
            "vocab": ["base_vocab.json", "math_vocab.json"]
        },
        "embedding": ["__init__.py", "token_embeddings.py", "positional_embeddings.py", "embedding_utils.py"],
        "transformer": ["__init__.py", "decoder.py", "attention.py", "feed_forward.py", "layer_norm.py", "model.py"],
        "generation": ["__init__.py", "language_head.py", "sampler.py", "beam_search.py", "reasoning_engine.py"],
        "tools": {
            "__init__.py": None,
            "base_tool.py": None,
            "tool_router.py": None,
            "tool_registry.py": None,
            "symbolic": ["__init__.py", "sympy_solver.py", "algebra_solver.py"],
            "numerical": ["__init__.py", "numpy_calculator.py", "scipy_solver.py"],
            "visualization": ["__init__.py", "matplotlib_plotter.py", "graph_generator.py"],
            "external": ["__init__.py", "wolfram_alpha.py"],
            "execution": ["__init__.py", "code_executor.py", "sandbox.py"]
        },
        "output": ["__init__.py", "formatter.py", "latex_renderer.py", "result_aggregator.py"],
        "utils": ["__init__.py", "logger.py", "error_handler.py", "metrics.py"]
    },
    "api": {
        "__init__.py": None,
        "server.py": None,
        "routes": ["__init__.py", "solve.py", "health.py", "tools.py"],
        "middleware": ["__init__.py", "auth.py", "rate_limiter.py"]
    },
    "training": ["__init__.py", "trainer.py", "dataset.py", "losses.py", "optimizers.py", "callbacks.py"],
    "data": {
        "raw": {
            "math_problems": [".gitkeep"],
            "solutions": [".gitkeep"]
        },
        "processed": {
            "tokenized": [".gitkeep"],
            "embedded": [".gitkeep"]
        },
        "samples": ["test_cases.json"]
    },
    "models": {
        "checkpoints": [".gitkeep"],
        "pretrained": [".gitkeep"],
        "exports": [".gitkeep"]
    },
    "tests": {
        "__init__.py": None,
        "unit": ["test_input_processing.py", "test_tokenization.py", "test_transformer.py", "test_tools.py", "test_generation.py"],
        "integration": ["test_end_to_end.py", "test_tool_calling.py"],
        "fixtures": ["sample_problems.json", "expected_outputs.json"]
    },
    "notebooks": {
        "exploration": ["data_analysis.ipynb", "model_analysis.ipynb"],
        "demos": ["solving_demo.ipynb"]
    },
    "scripts": ["train.py", "evaluate.py", "inference.py", "export_model.py", "setup_tools.py"],
    "docs": ["architecture.md", "api_reference.md", "tool_development.md", "deployment.md"],
    "docker": ["Dockerfile", "docker-compose.yml", "requirements.txt"]
}

def create_structure(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        
        if isinstance(content, dict):
            # It's a directory with subdirectories/files
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        elif isinstance(content, list):
            # It's a directory with files
            os.makedirs(path, exist_ok=True)
            for file in content:
                file_path = os.path.join(path, file)
                open(file_path, 'a').close()
        elif content is None:
            # It's a single file
            open(path, 'a').close()

# Create root files
root_files = ["README.md", "requirements.txt", "setup.py", ".env.example", ".gitignore"]
for file in root_files:
    open(file, 'a').close()

# Create the structure
create_structure(".", structure)

print("✅ File structure created successfully!")
print("📂 Open the folder in VS Code with: code .")