import re
from typing import Dict

CRITERIA = ["Originality", "Methodology", "References", "Structure", "Ethics"]


def score_manuscript(text: str) -> Dict[str, int]:
    """Return a dict with per-criterion scores (0-20) and total (0-100).

    Deterministic, rule-based scoring suitable for unit tests.
    """
    t = (text or "").lower()
    words = re.findall(r"\w+", t)
    word_count = len(words)
    unique_ratio = (len(set(words)) / word_count) if word_count else 0.0

    # Originality: presence of keywords + unique ratio
    originality_kw = any(k in t for k in ["novel", "original", "innovative", "contribution"])
    originality = min(20, int((10 if originality_kw else 0) + unique_ratio * 10))

    # Methodology: presence of method-related keywords
    methodology_kw = any(k in t for k in ["method", "methodology", "experiment", "procedure", "survey", "study"]) 
    # Give full points if clear methodology keywords are present
    methodology = 20 if methodology_kw else 5

    # References: look for years (recent refs) or 'references' section
    years = re.findall(r"\b(19\d{2}|20\d{2})\b", t)
    recent = any(int(y) >= 2018 for y in years) if years else False
    references = 20 if recent or ('references' in t) else 5

    # Structure: check for common sections
    sections = sum(1 for s in ["abstract", "introduction", "method", "results", "discussion", "conclusion"] if s in t)
    structure = min(20, int((sections / 6) * 20))

    # Ethics: presence of 'ethic' and 'informed consent' or similar
    ethics_kw = any(k in t for k in ["ethic", "informed consent", "approval", "consent"]) 
    ethics = 20 if ethics_kw else 10

    scores = {
        "Originality": originality,
        "Methodology": methodology,
        "References": references,
        "Structure": structure,
        "Ethics": ethics,
    }
    scores["Total"] = sum(scores[c] for c in CRITERIA)
    return scores
