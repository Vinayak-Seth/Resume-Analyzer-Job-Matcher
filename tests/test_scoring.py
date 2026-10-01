from src.scoring import evidence_is_verbatim, keyword_baseline, verdict_for

CFG = {"strong_fit_min": 75, "moderate_fit_min": 50}


def test_verdict_thresholds():
    assert verdict_for(80, CFG) == "Strong fit"
    assert verdict_for(60, CFG) == "Moderate fit"
    assert verdict_for(20, CFG) == "Weak fit"


def test_keyword_baseline():
    assert keyword_baseline("Knows Python and SQL", ["python", "SQL", "Spark", "AWS"]) == 50
    assert keyword_baseline("anything", []) == 0


def test_evidence_check():
    resume = "Built a churn model\nusing scikit-learn."
    assert evidence_is_verbatim("churn model using scikit-learn", resume)
    assert not evidence_is_verbatim("led a team of 10 engineers", resume)
    assert evidence_is_verbatim("", resume)
