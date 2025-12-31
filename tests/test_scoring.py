from scoring import score_manuscript


def test_score_perfect_sample():
    text = """
    Abstract
    This novel study presents an original contribution.
    Introduction
    Methods
    We describe the method and experiment.
    Results
    Discussion
    Conclusion
    References
    Smith et al. (2021)
    Ethics approval obtained. Informed consent.
    """
    scores = score_manuscript(text)
    assert scores['Originality'] == 20
    assert scores['Methodology'] == 20
    assert scores['References'] == 20
    assert scores['Structure'] == 20
    assert scores['Ethics'] == 20
    assert scores['Total'] == 100
