import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scorer import compute_score
from parser import tokenize, _clean_text


# ── tokenizer tests ───────────────────────────────────────────────────────────

def test_tokenize_basic():
    tokens = tokenize("Python developer with Docker experience")
    assert "python" in tokens
    assert "docker" in tokens
    assert "with" not in tokens           # stopword

def test_tokenize_removes_punctuation():
    tokens = tokenize("Java, C++, and SQL.")
    assert "java" in tokens
    assert "sql"  in tokens

def test_tokenize_empty():
    assert tokenize("") == []

def test_clean_text_strips_whitespace():
    assert _clean_text("  hello   world  ") == "hello world"


# ── scorer tests ─────────────────────────────────────────────────────────────

def test_perfect_match():
    jd     = "Python Flask Docker Kubernetes CI/CD REST API"
    resume = "Python Flask Docker Kubernetes CI/CD REST API experienced developer"
    result = compute_score(resume, jd)
    assert result["score"] >= 80
    assert "Selected" in result["status"]

def test_no_match():
    jd     = "Java Spring Boot Microservices Oracle Database"
    resume = "Graphic designer Photoshop Illustrator branding logo"
    result = compute_score(resume, jd)
    assert result["score"] < 60
    assert "Rejected" in result["status"]

def test_partial_match():
    jd     = "Python Django REST API PostgreSQL Redis Celery"
    resume = "Python developer with REST API experience"
    result = compute_score(resume, jd)
    assert 0 < result["score"] < 100

def test_score_in_range():
    result = compute_score("software developer python", "python developer flask")
    assert 0 <= result["score"] <= 100

def test_result_has_required_keys():
    result = compute_score("python developer", "python flask developer")
    for key in ["score", "status", "matched", "missing", "total_jd_kw"]:
        assert key in result

def test_empty_jd_raises():
    with pytest.raises(ValueError):
        compute_score("python developer", "")

def test_matched_keywords_are_subset():
    jd     = "python flask docker kubernetes"
    resume = "python developer with flask experience"
    result = compute_score(resume, jd)
    jd_kws = set(tokenize(jd))
    for kw in result["matched"]:
        assert kw in jd_kws

def test_threshold_boundary():
    # Score at exactly boundary should be selected
    jd     = "python flask"
    resume = "python flask docker kubernetes aws devops ci cd jenkins"
    result = compute_score(resume, jd)
    assert result["score"] >= 60
