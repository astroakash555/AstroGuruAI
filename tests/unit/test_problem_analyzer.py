"""Problem Analyzer unit tests."""

import json

from ai_engine.analyzers.problem import ProblemAnalyzer, ProblemAnalyzerInput
from ai_engine.analyzers.problem.constants import ProblemCategory


def test_marriage_problem_detection():
    analyzer = ProblemAnalyzer()
    result = analyzer.analyze_text("I am facing severe delay in marriage and relationship issues with my partner.")

    assert result.category.category == ProblemCategory.MARRIAGE
    assert 7 in result.houses.primary
    assert "Venus" in result.planets.primary
    assert result.severity.score >= 0.5
    assert len(result.root_cause_indicators) >= 1
    assert all("remedy" not in item.indicator.lower() for item in result.root_cause_indicators)


def test_business_loss_detection():
    analyzer = ProblemAnalyzer()
    result = analyzer.analyze_text("My business is facing major loss and financial crisis due to debt.")

    assert result.category.category == ProblemCategory.BUSINESS_FINANCE
    assert 2 in result.houses.primary or 11 in result.houses.primary
    assert "Saturn" in result.planets.primary or "Mercury" in result.planets.primary
    assert result.severity.level in {"high", "critical", "moderate"}


def test_court_case_detection():
    analyzer = ProblemAnalyzer()
    result = analyzer.analyze_text("I have an ongoing court case and legal dispute with my business partner.")

    assert result.category.category == ProblemCategory.LEGAL
    assert 6 in result.houses.primary or 6 in result.houses.secondary
    assert "Saturn" in result.planets.primary or "Mars" in result.planets.primary


def test_unknown_problem_detection():
    analyzer = ProblemAnalyzer()
    result = analyzer.analyze_text("I have an unknown problem and I am not sure what is wrong.")

    assert result.category.category == ProblemCategory.UNKNOWN
    assert 6 in result.houses.secondary
    assert result.severity.score <= 0.5


def test_json_output_structure():
    analyzer = ProblemAnalyzer()
    payload = analyzer.analyze_json(
        ProblemAnalyzerInput(problem_text="Marriage issues and conflict with spouse.")
    )

    assert payload["category"]["category"] == "marriage"
    assert "houses" in payload
    assert "planets" in payload
    assert "severity" in payload
    assert "root_cause_indicators" in payload
    assert payload["metadata"]["ai_ready"] is True
    assert "remedy" not in json.dumps(payload).lower()

    # Validate JSON serializable
    json.dumps(payload)
