import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Load API Key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def get_router_chain():
    # Initialize Gemini Flash (Fast & Cheap)
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-preview-09-2025",
        google_api_key=GOOGLE_API_KEY, 
        temperature=0
    )

    # The "Manager" Prompt
    template = """
    You are a Math Assistant Manager.
    
    Current Conversation History:
    {history}
    
    User's New Input: {input}
    
    YOUR JOB:
    1. DECIDE: Is this a math problem? Or just a casual greeting ("hello", "thanks")?
    2. REFINE: If the user refers to past context (e.g., "solve that", "what if x is 5?"), rewrite the question to be a full, standalone math problem.
    3. ROUTE: Return a JSON with "type" and "content".

    EXAMPLES:
    - Input: "Hello" -> {{"type": "chat", "content": "Hello! I am ready to help you with math."}}
    - Input: "Solve x + 5 = 10" -> {{"type": "math", "content": "Solve x + 5 = 10"}}
    - History: "Integral of x", Input: "What about x^2?" -> {{"type": "math", "content": "Calculate the integral of x^2"}}

    OUTPUT (JSON ONLY):
    """
    
    prompt = PromptTemplate(template=template, input_variables=["history", "input"])
    return LLMChain(llm=llm, prompt=prompt)