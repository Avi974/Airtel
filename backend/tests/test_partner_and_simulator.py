"""
Unit tests for Heuristic Priority Index (HPI) scoring and Simulator Milestone transitions.
"""

from app.partner.service import calculate_hpi_score
from app.routers.simulator import VALID_TRANSITIONS, MILESTONE_TITLES


def test_hpi_score_formula():
    # Micro lead with no GSTIN, low budget -> low score
    score_low = calculate_hpi_score(
        has_gstin=False,
        monthly_budget_inr=1500,
        segment="micro",
        employee_count=2,
        reached_quote=False,
        num_sites=1,
    )
    assert score_low == 0

    # High-value Professional lead with verified GSTIN and accepted quote
    score_high = calculate_hpi_score(
        has_gstin=True,          # +35
        monthly_budget_inr=6000, # +25
        segment="prof",
        employee_count=6,        # +20
        reached_quote=True,      # +20
        num_sites=2,
    )
    assert score_high == 100


def test_simulator_milestones_aligned_with_db_enum():
    # Check that all simulator milestones are recognized in the target enum
    for milestone in ["SURVEY_SCHEDULED", "INSTALL_IN_PROGRESS", "ACTIVE"]:
        assert milestone in MILESTONE_TITLES
        title, detail = MILESTONE_TITLES[milestone]
        assert len(title) > 0
        assert len(detail) > 0

    # Check forward progression graph
    assert "SURVEY_SCHEDULED" in VALID_TRANSITIONS["READY_FOR_FULFILMENT"]
    assert "INSTALL_IN_PROGRESS" in VALID_TRANSITIONS["SURVEY_SCHEDULED"]
    assert "ACTIVE" in VALID_TRANSITIONS["INSTALL_IN_PROGRESS"]
