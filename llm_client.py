"""
Thin wrapper around the Anthropic API for two roles:

  generate_answer(question, context_chunks) -> the "system under test" answer,
      grounded only in the retrieved context (this is the RAG generation step).

  judge_answer(question, answer, context_chunks) -> a SECOND LLM call that scores
      the first answer. This is the "LLM-as-a-judge" pattern: one model produces
      an answer, a separate call evaluates it against a rubric, independent of
      whether a human ever reads the raw output.

Requires ANTHROPIC_API_KEY to be set in the environment.
"""

import json
import os
import anthropic

MODEL = "claude-sonnet-4-6"

_client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def _format_context(chunks) -> str:
    if not chunks:
        return "(no relevant context was retrieved)"
    return "\n\n---\n\n".join(f"[{c.doc_id}]\n{c.text}" for c in chunks)


def generate_answer(question: str, chunks) -> str:
    context = _format_context(chunks)
    system = (
        "Answer the user's question using ONLY the information in the provided "
        "context. If the context does not contain the answer, say plainly that "
        "you don't have information on that in the provided documents. Do not "
        "use outside knowledge, and do not guess."
    )
    prompt = f"Context:\n{context}\n\nQuestion: {question}"
    resp = _client.messages.create(
        model=MODEL,
        max_tokens=400,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text.strip()


JUDGE_SYSTEM = """You are an evaluator scoring a RAG (retrieval-augmented generation) system's
answer. You will be given the retrieved context, the question, and the answer produced by the
system under test. Score strictly against the rubric below and return ONLY valid JSON, no
markdown fences, no preamble.

Rubric:
- groundedness (0.0-1.0): does every factual claim in the answer trace back to the provided
  context? 1.0 means fully supported. Lower scores mean some or all claims are not backed by
  the context.
- hallucination_detected (true/false): true if the answer states something as fact that is not
  present in or is contradicted by the context.
- correctly_declined (true/false): true if the context does not contain the answer AND the
  system correctly said it didn't know, rather than guessing. false if this case doesn't apply
  (context did contain the answer).
- reasoning: one or two sentences explaining the score.

Return exactly this JSON shape:
{"groundedness": 0.0, "hallucination_detected": false, "correctly_declined": false, "reasoning": ""}
"""


def judge_answer(question: str, answer: str, chunks) -> dict:
    context = _format_context(chunks)
    prompt = (
        f"Context:\n{context}\n\nQuestion: {question}\n\nSystem's answer: {answer}\n\n"
        "Score this answer per the rubric."
    )
    resp = _client.messages.create(
        model=MODEL,
        max_tokens=300,
        system=JUDGE_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = resp.content[0].text.strip()
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "groundedness": 0.0,
            "hallucination_detected": True,
            "correctly_declined": False,
            "reasoning": f"Judge returned unparseable output: {raw[:200]}",
        }
