from __future__ import annotations
from typing import List, Dict, Optional
import re
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.file_store import get_file_by_name

_SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")

def _basic_language_detect(text: str) -> str:
    # Minimal heuristic to avoid new deps; default to 'en'
    # If it contains many accented chars, guess 'hu' or 'de' etc. This is a placeholder.
    return "en"

def split_into_sentences(text: str) -> List[str]:
    text = text.replace("\r", " ").replace("\n", " ").strip()
    # Collapse spaces
    text = re.sub(r"\s+", " ", text)
    if not text:
        return []
    parts = _SENT_SPLIT_RE.split(text)
    # Filter very short fragments
    return [p.strip() for p in parts if len(p.strip()) >= 3]

async def load_text_from_file(session: AsyncSession, file_id: str) -> Optional[str]:
    rec = await get_file_by_name(session, file_id)
    if not rec:
        return None
    try:
        return rec.data.decode("utf-8", errors="ignore")
    except Exception:
        # Fallback: keep raw bytes repr
        return None

async def preprocess_text(session: AsyncSession, raw_text: Optional[str] = None, file_id: Optional[str] = None) -> List[Dict]:
    """Return a list of sentence dicts: {"text": ..., "lang": ...}. If file_id is provided, it is used."""
    if file_id and not raw_text:
        raw_text = await load_text_from_file(session, file_id)
    if not raw_text:
        return []
    lang = _basic_language_detect(raw_text)
    sentences = split_into_sentences(raw_text)
    return [{"text": s, "lang": lang} for s in sentences]

