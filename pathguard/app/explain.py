
import textwrap

_HF_SUMMARIZER = None  # cached HF pipeline


def _rule_based_explain(segments):
    # Derive top reasons across segments (very simple aggregation)
    reasons = []
    for s in segments:
        reasons.extend(s.get("reasons", []))
    if not reasons:
        return "No specific risk factors detected on this toy route."
    top = {}
    for r in reasons:
        top[r] = top.get(r, 0) + 1
    top_sorted = sorted(top.items(), key=lambda x: x[1], reverse=True)[:3]
    bullets = ", ".join([f"{k} (x{v})" for k, v in top_sorted])
    return f"This route's score is influenced by: {bullets}."


def explain_route(segments, use_hf: bool = False) -> str:
    # Placeholder for a future HF model; rule-based by default for speed/reliability
    # If you hook in a small HF model, you can call it here.
    if use_hf:
        global _HF_SUMMARIZER
        try:
            if _HF_SUMMARIZER is None:
                from transformers import pipeline
                _HF_SUMMARIZER = pipeline("summarization", model="t5-small")
            text = _rule_based_explain(segments)
            # Keep summary short for UI
            result = _HF_SUMMARIZER(text, max_length=50, min_length=10, do_sample=False)
            if isinstance(result, list) and result:
                return result[0].get("summary_text", text)
            return text
        except Exception:
            # Safe fallback if transformers is not available or fails at runtime
            return _rule_based_explain(segments)
    return _rule_based_explain(segments)
