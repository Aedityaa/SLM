import json
import re
from langchain.memory import ConversationBufferWindowMemory
from src.input_processing.router import get_router_chain
from src.generation.inference import MathSolverInference
from src.output.formatter import clean_latex

class MathAgent:
    def __init__(self):
        # We use return_messages=False so we get a string history, not objects
        self.memory = ConversationBufferWindowMemory(k=3, return_messages=False)
        self.router = get_router_chain()
        self.worker = MathSolverInference() 

    def run(self, user_input, max_tokens=2048):
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
                max_tokens=max_tokens 
            )
            raw_math = result_dict['solution'] 
            
            # Clean up the LaTeX delimiters ($$) for the frontend
            response = clean_latex(raw_math)

        # 4. Save to Memory
        self.memory.save_context({"input": user_input}, {"output": response})
        
        return response