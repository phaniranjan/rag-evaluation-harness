"""
Run the golden dataset end to end:

  question -> retrieve context -> generate answer -> judge answer -> record score

Then aggregate, because a single noisy run isn't a reliable regression signal
for a non-deterministic system. Compare the aggregate groundedness / hallucination
rate against a threshold, the same "tiered gating on distributions, not individual
runs" idea used for evaluating non-deterministic LLM outputs.

Usage:
    export GEMINI_API_KEY=...
    python run_eval.py
"""

import json
import os
import sys

from retrieval import Retriever
from llm_client import generate_answer, judge_answer

GROUNDEDNESS_THRESHOLD = 0.7


def main():
    if not os.environ.get("GEMINI_API_KEY"):
        print("ERROR: set GEMINI_API_KEY before running.", file=sys.stderr)
        sys.exit(1)

    base_dir = os.path.dirname(__file__)
    retriever = Retriever(os.path.join(base_dir, "corpus"))
    with open(os.path.join(base_dir, "golden_dataset.json")) as f:
        golden_set = json.load(f)

    results = []
    print(f"Running {len(golden_set)} cases...\n")

    for item in golden_set:
        chunks = retriever.retrieve(item["question"], k=3)
        answer = generate_answer(item["question"], chunks)
        judgment = judge_answer(item["question"], answer, chunks)

        result = {
            "id": item["id"],
            "question": item["question"],
            "expected_answerable": item["expected_answerable"],
            "answer": answer,
            **judgment,
        }
        results.append(result)

        status = "PASS" if judgment["groundedness"] >= GROUNDEDNESS_THRESHOLD else "FAIL"
        flag = " [HALLUCINATION]" if judgment["hallucination_detected"] else ""
        print(f"{item['id']} [{status}]{flag}  groundedness={judgment['groundedness']:.2f}")
        print(f"  Q: {item['question']}")
        print(f"  A: {answer[:150]}{'...' if len(answer) > 150 else ''}")
        print(f"  judge: {judgment['reasoning']}\n")

    # --- aggregate report, not per-run gating ---
    n = len(results)
    avg_groundedness = sum(r["groundedness"] for r in results) / n
    hallucination_rate = sum(r["hallucination_detected"] for r in results) / n

    trap_cases = [r for r in results if not r["expected_answerable"]]
    correctly_declined = sum(r["correctly_declined"] for r in trap_cases)

    print("=" * 60)
    print("AGGREGATE REPORT")
    print("=" * 60)
    print(f"Cases run:                {n}")
    print(f"Avg groundedness:         {avg_groundedness:.3f}  (threshold: {GROUNDEDNESS_THRESHOLD})")
    print(f"Hallucination rate:       {hallucination_rate:.1%}")
    print(f"Trap cases (unanswerable): {len(trap_cases)}")
    print(f"  Correctly declined:     {correctly_declined}/{len(trap_cases)}")

    overall = "PASS" if avg_groundedness >= GROUNDEDNESS_THRESHOLD else "FAIL"
    print(f"\nOverall: {overall}")

    with open(os.path.join(base_dir, "last_run_results.json"), "w") as f:
        json.dump(results, f, indent=2)
    print("\nFull results written to last_run_results.json")


if __name__ == "__main__":
    main()
