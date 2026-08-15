from pathlib import Path

from app.evidence.extractor import extract_clinical_evidence
from app.evidence.matcher import match_evidence_to_criteria
from app.retrieval.policy_loader import load_policy


def test_policy_matching():
    patient = {
        "patient_id": "PAT-1001",
        "age": 58,
        "gender": "female",

        "conditions": [
            {
                "code": "M54.16",
                "description": "Lumbar radiculopathy",
                "status": "active",
            }
        ],

        "medications": [
            {
                "name": "Naproxen",
                "status": "completed",
                "duration_weeks": 6,
            }
        ],

        "procedures": [
            {
                "code": "97110",
                "description": "Physical therapy",
                "date": "2026-07-01",
            }
        ],

        "observations": [
            {
                "name": "Pain score",
                "value": 8,
                "unit": "/10",
            }
        ],

        "encounters": [
            {
                "type": "outpatient",
                "date": "2026-07-20",
                "reason": "Persistent lower-back pain",
            }
        ],
    }

    evidence = extract_clinical_evidence(patient)

    project_root = Path(__file__).resolve().parents[2]

    policy_path = (
        project_root
        / "policies"
        / "sample"
        / "lumbar_mri_policy.json"
    )

    policy = load_policy(policy_path)

    results = match_evidence_to_criteria(
        evidence=evidence,
        policy=policy,
    )

    assert len(results) == 4

    assert results[0]["status"] == "MET"
    assert results[1]["status"] == "MET"
    assert results[2]["status"] == "MET"
    assert results[3]["status"] == "MET"

    assert results[0]["met"] is True
    assert results[3]["source"] == "SAMPLE-LUMBAR-MRI-001"