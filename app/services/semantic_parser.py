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
    # Direct patterns (X verb Y)
    (re.compile(r"(\b\w[\w\s]+?)\s+(increases|raises|amplifies|boosts|leads to|causes|triggers)\s+([\w\s]+?)\b", re.I), "+"),
    (re.compile(r"(\b\w[\w\s]+?)\s+(reduces|decreases|lowers|mitigates|diminishes)\s+([\w\s]+?)\b", re.I), "-"),
    # Participial phrases (X, verbing Y or X is verbing Y)
    (re.compile(r"(\b\w[\w\s]+?)\s*[,]\s*(?:is|are|was|were)?\s*(increasing|raising|amplifying|boosting|leading to|causing|triggering)\s+([\w\s]+?)\b", re.I), "+"),
    (re.compile(r"(\b\w[\w\s]+?)\s*[,]\s*(?:is|are|was|were)?\s*(reducing|decreasing|lowering|mitigating|diminishing)\s+([\w\s]+?)\b", re.I), "-"),
    # Impact/affect patterns (usually negative)
    (re.compile(r"(\b\w[\w\s]+?)\s+impacts?\s+([\w\s]+?)\b", re.I), "-"),
    (re.compile(r"(\b\w[\w\s]+?)\s*[,]\s*(?:is|are|was|were)?\s*impacting\s+([\w\s]+?)\b", re.I), "-"),
    (re.compile(r"(\b\w[\w\s]+?)\s+affects?\s+([\w\s]+?)\b", re.I), "-"),
    (re.compile(r"(\b\w[\w\s]+?)\s*[,]\s*(?:is|are|was|were)?\s*affecting\s+([\w\s]+?)\b", re.I), "-"),
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
        # First try standard patterns
        for rx, sign in REL_PATTERNS:
            m = rx.search(text)
            if m:
                cause = m.group(1).strip().lower()
                effect = m.group(2).strip().lower() if len(m.groups()) == 2 else m.group(3).strip().lower()
                # Clean up cause - limit to reasonable length (max 4 words before comma/verb)
                cause_words = cause.split()[:4]
                cause = " ".join(cause_words)
                triples.append({"cause": cause, "effect": effect, "sign": "+" if sign=="+" else "-", "confidence": 0.7})
        
        # Additional pattern for participial phrases: look for comma + participle + entity
        # Pattern: ", (reducing|impacting|affecting) entity"
        participial_pattern = re.compile(r",\s*(reducing|decreasing|impacting|affecting|increasing|raising)\s+([\w\s]+?)(?:\s+and|\s*\.|$)", re.I)
        for m in participial_pattern.finditer(text):
            verb = m.group(1).lower()
            effect = m.group(2).strip().lower()
            # Try to find the cause entity before the comma
            # Look for entity keywords from DOMAIN_KEYWORDS in the text before the comma
            before_comma = text[:m.start()].lower()
            cause_found = None
            last_match_pos = -1
            # Check all entity keywords and find the most recent one before the comma
            for domain, patterns in DOMAIN_KEYWORDS.items():
                for pat in patterns:
                    matches = list(re.finditer(pat, before_comma, re.I))
                    if matches:
                        # Take the last (most recent) match before the comma
                        last_match = matches[-1]
                        if last_match.end() > last_match_pos:
                            last_match_pos = last_match.end()
                            cause_found = last_match.group(0).lower()
            
            if cause_found:
                sign = "-" if verb in ["reducing", "decreasing", "impacting", "affecting"] else "+"
                triples.append({"cause": cause_found, "effect": effect, "sign": sign, "confidence": 0.7})
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

