from app.evidence.readiness import calculate_readiness


def test_readiness_all_criteria_met():
    results = [
        {"criterion_id": "C1", "status": "MET"},
        {"criterion_id": "C2", "status": "MET"},
        {"criterion_id": "C3", "status": "MET"},
        {"criterion_id": "C4", "status": "MET"},
    ]

    readiness = calculate_readiness(results)

    assert readiness["readiness_score"] == 100
    assert readiness["criteria_met"] == 4
    assert readiness["criteria_total"] == 4
    assert readiness["status"] == "READY_FOR_REVIEW"
    assert readiness["missing_evidence"] == []


def test_readiness_with_missing_evidence():
    results = [
        {
            "criterion_id": "C1",
            "criterion": "Persistent symptoms",
            "status": "MET",
        },
        {
            "criterion_id": "C2",
            "criterion": "Medication therapy",
            "status": "MET",
        },
        {
            "criterion_id": "C3",
            "criterion": "Physical therapy",
            "status": "INSUFFICIENT",
            "notes": "No physical therapy documentation found.",
        },
        {
            "criterion_id": "C4",
            "criterion": "Relevant diagnosis",
            "status": "MET",
        },
    ]

    readiness = calculate_readiness(results)

    assert readiness["readiness_score"] == 75
    assert readiness["criteria_met"] == 3
    assert readiness["status"] == "NEARLY_READY"

    assert len(readiness["missing_evidence"]) == 1
    assert readiness["missing_evidence"][0]["criterion_id"] == "C3"