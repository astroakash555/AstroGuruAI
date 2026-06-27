"""Knowledge brain tests."""

from __future__ import annotations

import json

import pytest

from knowledge_brain import KnowledgeQuery, KnowledgeRegistry, KnowledgeSearchEngine
from knowledge_brain.builders.build_all import build_all
from knowledge_brain.loader import KnowledgeLoader


@pytest.fixture(scope="module")
def knowledge_root(tmp_path_factory):
    root = tmp_path_factory.mktemp("knowledgebase")
    build_all(root)
    return root


def test_manifest_and_counts(knowledge_root):
    manifest = json.loads((knowledge_root / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["version"] == "1.0"
    assert manifest["total_rule_count"] >= 900
    assert manifest["files"]["domains/marriage_rules.json"] >= 300
    assert manifest["files"]["domains/career_rules.json"] >= 300


def test_vedic_entity_counts(knowledge_root):
    loader = KnowledgeLoader(knowledge_root)
    planets = loader.load_entities("vedic/planets.json")
    houses = loader.load_entities("vedic/houses.json")
    signs = loader.load_entities("vedic/signs.json")
    nakshatras = loader.load_entities("vedic/nakshatras.json")
    padas = loader.load_entities("vedic/padas.json")

    assert len(planets) == 9
    assert len(houses) == 12
    assert len(signs) == 12
    assert len(nakshatras) == 27
    assert len(padas) == 108


def test_lal_kitab_and_kp_databases_exist(knowledge_root):
    loader = KnowledgeLoader(knowledge_root)
    lk = loader.load_lal_kitab_entries()
    kp = loader.load_kp_rules()
    assert len(lk["rin"]) >= 20
    assert len(lk["dosh"]) >= 20
    assert len(lk["remedies"]) >= 100
    assert len(lk["planet_house"]) >= 100
    assert len(kp["event_rules"]) >= 90
    assert len(kp["significator_rules"]) >= 48


def test_knowledge_search_marriage_delay(knowledge_root):
    engine = KnowledgeSearchEngine(KnowledgeRegistry(KnowledgeLoader(knowledge_root)))
    result = engine.search(
        KnowledgeQuery(
            problem_text="I am facing severe delay in marriage and relationship issues.",
            domain="marriage",
            category="delayed_marriage",
            planets=("Saturn", "Venus"),
            houses=(7,),
            max_results=10,
        )
    )
    payload = engine.search_json(
        KnowledgeQuery(
            problem_text="delay in marriage",
            domain="marriage",
            category="delayed_marriage",
            planets=("Saturn",),
            houses=(7,),
            max_results=5,
        )
    )

    assert result.ranked_rules
    assert result.summary["matched_rule_count"] >= 1
    assert payload["metadata"]["ai_prediction"] is False
    assert json.dumps(payload)


def test_knowledge_search_infers_career_domain(knowledge_root):
    engine = KnowledgeSearchEngine(KnowledgeRegistry(KnowledgeLoader(knowledge_root)))
    result = engine.search(
        KnowledgeQuery(problem_text="I lost my job and need government employment.")
    )
    assert result.summary["inferred_domain"] == "career"
    assert result.ranked_rules
