"""Focused tests for the LLM→DBN pipeline support modules."""

from __future__ import annotations

import os
import sqlite3
import sys
import types

import pytest

# Provide a default in-memory database URL so settings can initialise during imports.
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

# SQLAlchemy only needs a subset of the aiosqlite interface during test imports.
if "aiosqlite" not in sys.modules:
    stub = types.ModuleType("aiosqlite")
    for name in (
        "DatabaseError",
        "Error",
        "IntegrityError",
        "NotSupportedError",
        "OperationalError",
        "ProgrammingError",
        "sqlite_version",
        "sqlite_version_info",
    ):
        setattr(stub, name, getattr(sqlite3, name))

    def _connect(*args, **kwargs):  # pragma: no cover - used only for import-time wiring
        class _Conn:
            daemon = True

        return _Conn()

    stub.connect = _connect
    sys.modules["aiosqlite"] = stub

from app.services.causal_skeleton import build_skeleton, to_dbn_spec
from app.services.llama_client import (
    get_llama_forecast,
    llm_extract_entities,
    llm_extract_relations,
)
from app.services.semantic_parser import extract_entities, extract_relations, score_context

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    """Force AnyIO to use the asyncio backend so additional dependencies aren't required."""
    return "asyncio"


async def test_llama_client_uses_mock_response_by_default():
    """The llama client should fall back to the deterministic mock response when no API is configured."""
    prompt = "A prolonged drought reduces crop yield and raises food prices."
    response = await get_llama_forecast(prompt, stage_configs={"Reconnaissance": {"weight": 1.0}})

    assert response["stage"] == "Exploitation"
    assert response["nodes"], "mock response should include nodes"
    assert response["edges"], "mock response should include edges"


async def test_llm_helper_extractors_return_lists():
    """LLM helper functions should be resilient when the mock endpoint is active."""
    sentences = [
        {"text": "A prolonged drought reduces crop yield.", "lang": "en"},
        {"text": "EU subsidies may follow.", "lang": "en"},
    ]

    entities = await llm_extract_entities(sentences)
    relations = await llm_extract_relations(sentences)

    assert isinstance(entities, list)
    assert isinstance(relations, list)


async def test_text_preprocessing_splits_sentences():
    """Raw text should be normalised into language-tagged sentence dictionaries."""
    raw_text = "A prolonged drought reduces crop yield. Food prices rise. EU subsidies may follow."

    module_name = "app.services.file_store"
    if module_name not in sys.modules:
        stub = types.ModuleType(module_name)

        async def _get_file_by_name(*_args, **_kwargs):
            return None

        stub.get_file_by_name = _get_file_by_name
        sys.modules[module_name] = stub

    from app.services.text_preprocessor import preprocess_text, split_into_sentences

    sentences = await preprocess_text(None, raw_text=raw_text)

    assert len(sentences) == 3
    assert all("text" in item and "lang" in item for item in sentences)
    assert split_into_sentences(raw_text) == [item["text"] for item in sentences]


async def test_semantic_parsing_identifies_entities_and_relations():
    """Rule-based semantic parser should surface drought-related entities and relations."""
    sentences = [
        {"text": "A prolonged drought reduces crop yield.", "lang": "en"},
        {"text": "Food prices rise significantly.", "lang": "en"},
    ]

    entities = await extract_entities(sentences)
    relations = await extract_relations(sentences)
    scored_relations = await score_context(relations)

    entity_names = {entity["entity"] for entity in entities}
    assert "drought" in entity_names
    assert any(name in {"crop yield", "yield"} for name in entity_names)

    assert scored_relations == relations
    assert any(rel["sign"] == "-" for rel in relations)


async def test_causal_skeleton_to_dbn_spec_alignment():
    """Skeleton builder should produce nodes/edges that survive conversion to a DBN spec."""
    entities = [
        {"entity": "drought", "domain": "Environment"},
        {"entity": "crop yield", "domain": "Economy"},
    ]
    relations = [
        {"cause": "drought", "effect": "crop yield", "sign": "-", "confidence": 0.8},
    ]

    skeleton = build_skeleton(entities, relations)
    spec = to_dbn_spec(skeleton)

    assert len(spec["nodes"]) == len(skeleton["nodes"])
    assert spec["edges"], "conversion should retain causal edges"
    assert all(edge["source"] != edge["target"] for edge in spec["edges"])