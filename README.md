# RAG Evaluation Harness (learning project)

A small, working prototype: retrieve context for a question, generate a grounded
answer, then use a second LLM call to judge that answer. Built to actually learn
these terms hands-on, not just recite them.

## What each piece is, in plain terms

- **RAG (retrieval-augmented generation):** instead of the LLM answering from its
  own memory, we first search a document set for relevant text (`retrieval.py`),
  and only give the LLM that retrieved text to answer from.
- **Groundedness:** does every claim in the answer trace back to the retrieved
  context? Scored 0.0-1.0 by the judge call.
- **Hallucination:** the model stating something as fact that isn't actually in
  the context (or contradicts it). `gd-009` and `gd-010` in the golden dataset
  are deliberate traps with no real answer in the corpus, to check whether the
  system says "I don't know" or invents an answer.
- **LLM-as-a-judge:** a second, separate LLM call scores the first call's answer
  against a rubric, instead of (or in addition to) a human reviewing it.
- **Golden dataset:** a fixed, known set of question/answer pairs used to check
  quality consistently over time (`golden_dataset.json`), rather than eyeballing
  outputs each time.
- **Tiered / aggregate gating:** because LLM outputs are non-deterministic, we
  don't fail the whole run on one bad answer. We look at the average groundedness
  and hallucination rate across the full set, the same way a single flaky test
  shouldn't block a release on its own.

## Setup

```bash
pip install -r requirements.txt
export GEMINI_API_KEY=...
python run_eval.py
```

## Files

- `corpus/` - sample source documents (generic networking topics, not tied to
  any employer's proprietary systems)
- `retrieval.py` - TF-IDF + cosine similarity retrieval (no external embedding
  API or model download needed; swap for a real embedding model later if you
  want to compare retrieval quality)
- `llm_client.py` - the generation call and the judge call
- `golden_dataset.json` - 10 test cases, including 2 deliberate unanswerable traps
- `run_eval.py` - runs everything, prints per-case results and an aggregate report

## Natural next steps (each one is a real, addable skill)

1. Swap TF-IDF for a real embedding model and compare retrieval quality.
2. Add a second retrieval strategy (e.g. keyword + vector hybrid) and compare.
3. Track results over time (append each run's aggregate to a CSV) to see drift.
4. Add a prompt-injection test case to the golden set (a document chunk that
   tries to instruct the model to ignore its system prompt) and confirm the
   generation step doesn't follow it - a basic guardrail check.
5. Try deliberately degrading the corpus (delete a doc) and confirm the
   hallucination rate on that topic goes up as expected - this is what
   validates that your judge is actually measuring something real.
