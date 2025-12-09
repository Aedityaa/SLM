"""Text generation with tool calling support"""
import torch
from typing import List, Dict, Optional
from src.tools.tool_router import ToolRouter

class MathGenerator:
    """Handles text generation with tool calling"""
    
    def __init__(self, model_wrapper):
        self.model_wrapper = model_wrapper
        self.model = model_wrapper.get_model()
        self.tokenizer = model_wrapper.get_tokenizer()
        self.device = model_wrapper.device
        self.tool_router = ToolRouter()
        self.max_tool_iterations = 5  # Prevent infinite loops
    
    def generate_with_tools(
        self,
        messages: List[Dict],
        max_new_tokens: int = 512,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict:
        """Generate with iterative tool calling"""
        
        conversation_history = messages.copy()
        tool_calls_made = []
        iteration = 0
        
        while iteration < self.max_tool_iterations:
            # Generate response
            raw_output = self.generate(
                conversation_history,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                **kwargs
            )
            
            answer = self.extract_answer(raw_output)
            
            # Check for tool calls
            if self.tool_router.detect_tool_call(answer):
                # Parse tool call
                tool_call = self.tool_router.parse_tool_call(answer)
                
                if tool_call:
                    # Execute tool
                    result = self.tool_router.execute_tool(tool_call)
                    tool_calls_made.append({
                        "tool": tool_call["tool_name"],
                        "params": tool_call["params"],
                        "result": result
                    })
                    
                    # Inject result back
                    answer_with_result = self.tool_router.inject_result(answer, result)
                    
                    # Add to conversation
                    conversation_history.append({
                        "role": "assistant",
                        "content": answer_with_result
                    })
                    
                    iteration += 1
                    continue
            
            # No more tool calls, we're done
            return {
                "final_answer": answer,
                "tool_calls": tool_calls_made,
                "iterations": iteration,
                "conversation": conversation_history
            }
        
        # Max iterations reached
        return {
            "final_answer": answer,
            "tool_calls": tool_calls_made,
            "iterations": iteration,
            "warning": "Max tool iterations reached",
            "conversation": conversation_history
        }
    
    def generate(
        self, 
        messages: List[Dict],
        max_new_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 50,
        do_sample: bool = True,
        repetition_penalty: float = 1.1
    ) -> str:
        """Generate response from messages"""
        
        # Format prompt using chat template
        formatted_prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        # Tokenize
        inputs = self.tokenizer(
            formatted_prompt,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=2048
        ).to(self.device)
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                do_sample=do_sample,
                repetition_penalty=repetition_penalty,
                eos_token_id=self.model_wrapper.get_eos_token_id(),
                pad_token_id=self.tokenizer.pad_token_id
            )
        
        # Decode
        generated_text = self.tokenizer.decode(
            outputs[0],
            skip_special_tokens=False
        )
        
        return generated_text
    
    def extract_answer(self, generated_text: str) -> str:
        """Extract just the assistant's response"""
        if "<|im_start|>assistant" in generated_text:
            answer = generated_text.split("<|im_start|>assistant")[-1]
            answer = answer.replace("<|im_end|>", "").strip()
            return answer
        return generated_text.strip()