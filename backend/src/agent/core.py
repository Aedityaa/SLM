import json
import re
import os
from langchain.memory import ConversationBufferWindowMemory
from src.input_processing.router import get_router_chain
from src.generation.inference import MathSolverInference
from src.output.formatter import clean_latex

class MathAgent:
    def __init__(self, enable_tools=True, enable_wolfram=True, wolfram_api_key=os.getenv('WOLFRAM_API_KEY')):
        # We use return_messages=False so we get a string history, not objects
        self.memory = ConversationBufferWindowMemory(k=3, return_messages=False)
        self.router = get_router_chain()
        if wolfram_api_key is None:
            wolfram_api_key = os.getenv('WOLFRAM_API_KEY')
        self.worker = MathSolverInference(
            enable_tools=enable_tools,
            enable_wolfram=enable_wolfram,
            wolfram_api_key=wolfram_api_key
        )
        self.enable_tools = enable_tools 
        self.enable_wolfram = enable_wolfram

    def run(self, user_input, max_tokens=2048, use_tools=None):
        print(f"🧠 Agent processing: {user_input}")
        
      
        history = self.memory.load_memory_variables({})['history']
        
        # 2. Manager Decides (Router)
        decision_raw = self.router.run(history=history, input=user_input)

        try:
            # 1. Clean Markdown wrappers
            clean_json = decision_raw.strip()
            if clean_json.startswith("```json"):
                clean_json = clean_json[7:]
            if clean_json.endswith("```"):
                clean_json = clean_json[:-3]
            clean_json = clean_json.strip()

            clean_json = re.sub(r'(?<!\\)\\(?![u"\\/bfnrt])', r'\\\\', clean_json)

            decision = json.loads(clean_json)

        except Exception as e:
            print(f"⚠️ JSON Parse Error: {e}. Raw: {decision_raw}")
         
            decision = {"type": "math", "content": user_input}

        response = ""
        
        # 3. Execution Logic
        if decision.get('type') == 'chat':
            print("💬 Routing to: General Chat")
            response = decision.get('content', "Hello!")
        else:
            print(f"🧮 Routing to: Math Worker -> {decision.get('content')}")
            
            # Use the REFINED content (which has the full context)
            result_dict = self.worker.solve(
                decision['content'],
                system_prompt="with_tools" if use_tools else "step_by_step",  
                max_tokens=max_tokens,
                use_tools=use_tools
            )
            raw_math = result_dict['solution'] 
            
            # Clean up the LaTeX delimiters ($$) for the frontend
            response = clean_latex(raw_math)

        # 4. Save to Memory
        self.memory.save_context({"input": user_input}, {"output": response})
        
        return response