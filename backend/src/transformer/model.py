"""Model loading with LoRA adapter support"""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel, PeftConfig
import os

class MathTransformerModel:
    """Wrapper for the Qwen2.5-Math model with LoRA"""
    
    def __init__(
        self, 
        base_model_id="Qwen/Qwen2.5-Math-1.5B-Instruct",
        lora_adapter_path=".\models\lora_adapter",  # Path to your fine-tuned LoRA weights
        device=None
    ):
        self.base_model_id = base_model_id
        self.lora_adapter_path = lora_adapter_path
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        
        print(f"🔄 Loading base model: {base_model_id}")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            base_model_id, 
            trust_remote_code=True,
            padding_side="left"
        )
        self.tokenizer.pad_token_id = self.tokenizer.eos_token_id
        
        # Load base model
        self.base_model = AutoModelForCausalLM.from_pretrained(
            base_model_id,
            torch_dtype=torch.bfloat16,
            trust_remote_code=True,
            device_map="auto" if torch.cuda.is_available() else None
        )
        
        # Load LoRA adapter if provided
        if lora_adapter_path and os.path.exists(lora_adapter_path):
            print(f"🔄 Loading LoRA adapter from: {lora_adapter_path}")
            self.model = PeftModel.from_pretrained(
                self.base_model,
                lora_adapter_path,
                torch_dtype=torch.bfloat16
            )
            print("✅ LoRA adapter loaded successfully!")
        else:
            self.model = self.base_model
            if lora_adapter_path:
                print(f"⚠️  LoRA path not found: {lora_adapter_path}")
                print("📌 Using base model without LoRA")
        
        self.model.eval()  # Set to evaluation mode
        print(f"✅ Model loaded on {self.device}")
    
    def get_model(self):
        """Return the model (with LoRA if loaded)"""
        return self.model
    
    def get_tokenizer(self):
        """Return the tokenizer"""
        return self.tokenizer
    
    def get_eos_token_id(self):
        """Get the end-of-sequence token ID"""
        return self.tokenizer.convert_tokens_to_ids("<|im_end|>")
    
    def merge_and_save(self, output_path):
        """Merge LoRA weights with base model and save"""
        if isinstance(self.model, PeftModel):
            print(f"🔄 Merging LoRA weights with base model...")
            merged_model = self.model.merge_and_unload()
            merged_model.save_pretrained(output_path)
            self.tokenizer.save_pretrained(output_path)
            print(f"✅ Merged model saved to: {output_path}")
        else:
            print("⚠️  No LoRA adapter to merge")