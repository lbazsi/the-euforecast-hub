from __future__ import annotations
from typing import List, Dict
import re
import logging
from app.services.llama_client import get_llama_forecast

logger = logging.getLogger(__name__)

DOMAIN_KEYWORDS = {
    "Environment": [r"drought", r"rainfall", r"temperature", r"emissions?", r"storm", r"flood"],
    "Economy": [r"price", r"gdp", r"exports?", r"imports?", r"market", r"employment", r"yield"],
    "Society": [r"unrest", r"migration", r"health", r"education", r"crime"],
    "Policy": [r"subsid(y|ies)", r"regulation", r"law", r"policy", r"ban", r"mandate"],
    "Technology": [r"ai", r"automation", r"innovation", r"infrastructure", r"network"]
}

REL_PATTERNS = [
    (re.compile(r"(\b\w[\w\s]+?)\s+(increases|raises|amplifies|boosts|leads to|causes)\s+([\w\s]+?)\b", re.I), "+"),
    (re.compile(r"(\b\w[\w\s]+?)\s+(reduces|decreases|lowers|mitigates)\s+([\w\s]+?)\b", re.I), "-")
]

def _guess_domain(term: str) -> str:
    t = term.lower()
    for d, patterns in DOMAIN_KEYWORDS.items():
        for pat in patterns:
            if re.search(pat, t):
                return d
    return "Environment"  # default

async def extract_entities(sentences: List[Dict]) -> List[Dict]:
    # Lightweight rule-based entity extraction; placeholder for LLM/NER
    ents = {}
    for s in sentences:
        text = s.get("text", "")
        for d, patterns in DOMAIN_KEYWORDS.items():
            for pat in patterns:
                for m in re.finditer(pat, text, re.I):
                    k = m.group(0).lower()
                    ents[k] = {"entity": k, "domain": d}
    return list(ents.values())

async def extract_relations(sentences: List[Dict]) -> List[Dict]:
    triples: List[Dict] = []
    for s in sentences:
        text = s.get("text", "")
        for rx, sign in REL_PATTERNS:
            m = rx.search(text)
            if m:
                cause = m.group(1).strip().lower()
                effect = m.group(3).strip().lower()
                triples.append({"cause": cause, "effect": effect, "sign": "+" if sign=="+" else "-", "confidence": 0.7})
    # Deduplicate simple
    seen = set()
    out = []
    for t in triples:
        key = (t["cause"], t["effect"], t["sign"])
        if key in seen: 
            continue
        seen.add(key)
        out.append(t)
    return out

async def score_context(triples: List[Dict]) -> List[Dict]:
    # Placeholder: already have confidence; could adjust with modal verbs, adverbs, etc.
    return triples

