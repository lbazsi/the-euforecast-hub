from __future__ import annotations
from typing import List, Dict, Optional
import re
from sqlalchemy.ext.asyncio import AsyncSession

try:  # pragma: no cover - import wiring validated via runtime behaviour
    from app.services import file_store as _file_store
except Exception:  # pragma: no cover - fall back to graceful degradation
    _file_store = None


async def _unavailable(*_args, **_kwargs):  # pragma: no cover - helper
    return None


_get_file_by_name = getattr(_file_store, "get_file_by_name", _unavailable)
_get_file_by_id = getattr(_file_store, "get_file_by_id", _unavailable)

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

async def load_text_from_file(session: AsyncSession, file_id_or_name: str) -> Optional[str]:
    """
    Load text from file, supporting both database ID and filename.
    Tries ID first, then falls back to filename lookup.
    """
    if session is None:
        return None

    rec = None
    if _get_file_by_id is not _unavailable:
        rec = await _get_file_by_id(session, file_id_or_name)
    if not rec and _get_file_by_name is not _unavailable:
        rec = await _get_file_by_name(session, file_id_or_name)
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