# """Deployment script"""
# import os
# import subprocess
# import sys

# def check_lora_model():
#     """Check if LoRA model exists"""
#     lora_path = os.getenv("LORA_ADAPTER_PATH", "./models/lora_adapter")
#     if not os.path.exists(lora_path):
#         print(f"⚠️  LoRA model not found at: {lora_path}")
#         print("📁 Please ensure your fine-tuned model is in the correct location")
#         return False
#     print(f"✅ LoRA model found at: {lora_path}")
#     return True

# def start_server(host="0.0.0.0", port=8000):
#     """Start the FastAPI server"""
#     if not check_lora_model():
#         sys.exit(1)
    
#     print(f"🚀 Starting server on {host}:{port}")
#     subprocess.run([
#         "uvicorn",
#         "api.server:app",
#         "--host", host,
#         "--port", str(port),
#         "--reload"
#     ])

# def start_docker():
#     """Start with Docker"""
#     if not check_lora_model():
#         sys.exit(1)
    
#     print("🐳 Starting with Docker...")
#     subprocess.run([
#         "docker-compose",
#         "-f", "docker/docker-compose.yml",
#         "up", "--build"
#     ])

# if __name__ == "__main__":
#     import argparse
    
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--mode", choices=["local", "docker"], default="local")
#     parser.add_argument("--host", default="0.0.0.0")
#     parser.add_argument("--port", type=int, default=8000)
    
#     args = parser.parse_args()
    
#     if args.mode == "docker":
#         start_docker()
#     else:
#         start_server(args.host, args.port)

"""Deployment script"""
import os
import subprocess
import sys

def check_lora_model():
    """Check if LoRA model exists and provide status"""
    lora_path = os.getenv("LORA_ADAPTER_PATH", "./models/lora_adapter")
    if not os.path.exists(lora_path):
        print(f"⚠️  LoRA model not found at: {lora_path}")
        # CHANGED: Informative message indicating fallback
        print("📌 Starting with BASE model only. Fine-tuning benefits will be unavailable.")
        return False
    print(f"✅ LoRA model found at: {lora_path}")
    return True

def start_server(host="0.0.0.0", port=8000):
    """Start the FastAPI server"""
    # ACTION: We call the check for logging, but remove the sys.exit(1)
    check_lora_model()
    
    print(f"🚀 Starting server on {host}:{port}")
    subprocess.run([
        "uvicorn",
        "api.server:app",
        "--host", host,
        "--port", str(port),
        "--reload"
    ])

def start_docker():
    """Start with Docker"""
    # ACTION: We call the check for logging, but remove the sys.exit(1)
    check_lora_model()
    
    print("🐳 Starting with Docker...")
    subprocess.run([
        "docker-compose",
        "-f", "docker/docker-compose.yml",
        "up", "--build"
    ])

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["local", "docker"], default="local")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    
    args = parser.parse_args()
    
    if args.mode == "docker":
        start_docker()
    else:
        start_server(args.host, args.port)