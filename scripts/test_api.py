"""Test the deployed API"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print("Health Check:", response.json())

def test_solve():
    """Test solve endpoint"""
    data = {
        "problem": "Find the value of x: 4x + 5 = 6x + 7",
        "max_tokens": 512,
        "temperature": 0.7
    }
    
    response = requests.post(f"{BASE_URL}/solve", json=data)
    result = response.json()
    
    print("\n=== Problem ===")
    print(result['problem'])
    print("\n=== Solution ===")
    print(result['solution'])
    print("\n=== Final Answer ===")
    print(result['final_answer'])

def test_batch():
    """Test batch solving"""
    data = {
        "problems": [
            "What is 2+2?",
            "Solve: x^2 = 16",
            "Find derivative of x^3"
        ]
    }
    
    response = requests.post(f"{BASE_URL}/solve-batch", json=data)
    results = response.json()
    
    print(f"\n=== Solved {results['count']} problems ===")
    for i, result in enumerate(results['results'], 1):
        print(f"\nProblem {i}: {result['problem']}")
        print(f"Answer: {result['final_answer']}")

if __name__ == "__main__":
    print("🧪 Testing Math Solver API...\n")
    test_health()
    test_solve()
    test_batch()
    print("\n✅ All tests completed!")