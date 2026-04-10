from parser import tokenize
from collections import Counter


def compute_score(resume_text: str, job_description: str) -> dict:
    """
    Compare resume text against a job description using keyword matching.

    Returns a dict with:
      - score       : int 0-100
      - status      : "Selected" or "Rejected"
      - matched     : list of matched keywords
      - missing     : list of important missing keywords
      - total_jd_kw : total unique keywords in JD
    """
    resume_tokens = set(tokenize(resume_text))
    jd_tokens     = tokenize(job_description)

    if not jd_tokens:
        raise ValueError("Job description appears to be empty after processing.")

    # Weighted frequency: keywords mentioned more in JD matter more
    jd_freq = Counter(jd_tokens)
    unique_jd_keywords = set(jd_freq.keys())

    if not unique_jd_keywords:
        raise ValueError("No meaningful keywords found in job description.")

    # --- Core match score (60 pts) ---
    matched_keywords = sorted(unique_jd_keywords & resume_tokens)
    missing_keywords = sorted(unique_jd_keywords - resume_tokens)

    base_ratio = len(matched_keywords) / len(unique_jd_keywords)
    base_score = base_ratio * 60

    # --- Weighted frequency bonus (25 pts) ---
    # Keywords that appear multiple times in JD are more important
    weighted_matched = sum(jd_freq[kw] for kw in matched_keywords)
    weighted_total   = sum(jd_freq.values())
    weighted_score   = (weighted_matched / weighted_total) * 25 if weighted_total else 0

    # --- Length & coverage bonus (15 pts) ---
    # Reward resumes with sufficient content (at least 100 tokens)
    resume_length_bonus = min(len(resume_tokens) / 150, 1.0) * 10
    # Small bonus for matching high-freq JD terms
    top_jd_kws = {kw for kw, _ in jd_freq.most_common(5)}
    top_match_bonus = len(top_jd_kws & resume_tokens) / max(len(top_jd_kws), 1) * 5

    total_score = int(min(base_score + weighted_score + resume_length_bonus + top_match_bonus, 100))

    status = "✅ Selected" if total_score >= 60 else "❌ Rejected"

    return {
        "score":        total_score,
        "status":       status,
        "matched":      matched_keywords[:20],   # cap display list
        "missing":      missing_keywords[:20],
        "total_jd_kw":  len(unique_jd_keywords),
        "resume_tokens": len(resume_tokens),
    }
