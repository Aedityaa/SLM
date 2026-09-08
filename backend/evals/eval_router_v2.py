"""
Router classification accuracy eval (math vs chat).
Matches the REAL interface in src/input_processing/router.py:
  get_router_chain() -> LLMChain expecting {history, input}, returning a raw JSON string.

Requires GOOGLE_API_KEY in your .env or environment.

Run:
    python eval_router.py
"""
import json
import re
import time
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.input_processing.router import get_router_chain

# Hand-labeled test set: (history, input_text, gold_label)
# history="" for standalone queries; non-empty to test context-dependent routing.
labeled_examples = [
    ("", "What is the derivative of x^2 + 3x?", "math"),
    ("", "Solve for x: 2x + 5 = 15", "math"),
    ("", "Can you plot y = sin(x) for me?", "math"),
    ("", "What's 15% of 340?", "math"),
    ("", "Integrate x^3 from 0 to 2", "math"),
    ("", "Hey, how's it going?", "chat"),
    ("", "What's the weather like today?", "chat"),
    ("", "Tell me a joke", "chat"),
    ("", "Who won the world cup in 2022?", "chat"),
    ("", "What's your favorite color?", "chat"),
    ("", "Simplify (x+1)(x-1)", "math"),
    ("", "What's 7 factorial?", "math"),
    ("", "Recommend a good math textbook", "chat"),
    ("", "Why does calculus even matter in real life?", "chat"),
    ("", "Compute the standard deviation of [2,4,4,4,5,5,7,9]", "math"),
    ("", "Good morning!", "chat"),
    # Context-dependent cases -- these specifically test the REFINE behavior
    # described in the router's own prompt template.
    ("User: Integral of x\nAssistant: The integral of x is x^2/2 + C", "What about x^2?", "math"),
    ("User: Solve x + 5 = 10\nAssistant: x = 5", "Can you solve that for me again?", "math"),
    ("User: What's the derivative of sin(x)?\nAssistant: cos(x)", "That's a cool function, can you explain it?", "chat"),
    ("User: Solve 2x = 8\nAssistant: x = 4", "What does x equal in the last problem?", "math"),
]

def extract_json(raw_text: str):
    """The router prompt asks for JSON-only output, but LLMs sometimes wrap it
    in markdown code fences or add stray text -- strip that defensively."""
    text = raw_text.strip()
    text = re.sub(r"^```(json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group(0)
    return json.loads(text)

def main():
    if not os.getenv("GOOGLE_API_KEY"):
        print("ERROR: GOOGLE_API_KEY not set. Add it to .env or `export GOOGLE_API_KEY=...` first.")
        sys.exit(1)

    chain = get_router_chain()

    results = []
    correct = 0
    latencies = []
    parse_failures = 0

    for history, text, gold_label in labeled_examples:
        t0 = time.perf_counter()
        pred_label = None
        raw_output = None
        try:
            raw_output = chain.run(history=history, input=text)
            parsed = extract_json(raw_output)
            pred_label = parsed.get("type")
        except json.JSONDecodeError:
            parse_failures += 1
            pred_label = "PARSE_ERROR"
        except Exception as e:
            pred_label = f"ERROR: {e}"
        latency = time.perf_counter() - t0
        latencies.append(latency)

        is_correct = pred_label == gold_label
        correct += int(is_correct)
        results.append({
            "history": history,
            "text": text,
            "gold": gold_label,
            "predicted": pred_label,
            "raw_output": raw_output,
            "correct": is_correct,
            "latency_s": round(latency, 3),
        })

    accuracy = correct / len(labeled_examples)
    avg_latency = sum(latencies) / len(latencies)

    print("=" * 70)
    print("ROUTER CLASSIFICATION EVAL")
    print("=" * 70)
    for r in results:
        status = "PASS" if r["correct"] else "FAIL"
        ctx = " [with context]" if r["history"] else ""
        print(f"[{status}] '{r['text'][:55]}'{ctx} -> pred={r['predicted']}, gold={r['gold']}")

    print(f"\nAccuracy: {correct}/{len(labeled_examples)} ({100*accuracy:.1f}%)")
    print(f"JSON parse failures: {parse_failures}/{len(labeled_examples)}")
    print(f"Avg latency: {avg_latency:.3f}s (Gemini API round-trip)")

    with open("router_eval_results.json", "w") as f:
        json.dump({
            "accuracy": accuracy,
            "parse_failure_rate": parse_failures / len(labeled_examples),
            "avg_latency_s": avg_latency,
            "results": results,
        }, f, indent=2)
    print("\nSaved to router_eval_results.json")

if __name__ == "__main__":
    main()
