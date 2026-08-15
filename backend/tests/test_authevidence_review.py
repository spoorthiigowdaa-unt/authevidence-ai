from pathlib import Path

from app.services.authevidence_review import run_authevidence_review


def test_authevidence_review():
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

    project_root = Path(__file__).resolve().parents[2]

    policy_path = (
        project_root
        / "policies"
        / "sample"
        / "lumbar_mri_policy.json"
    )

    result = run_authevidence_review(
        patient_data=patient,
        policy_path=policy_path,
    )

    assert result["patient_id"] == "PAT-1001"

    assert (
        result["policy"]["procedure_code"]
        == "72148"
    )

    assert len(result["criteria_assessment"]) == 4

    assert (
        result["authorization_readiness"]["readiness_score"]
        == 100
    )

    assert (
        result["authorization_readiness"]["status"]
        == "READY_FOR_REVIEW"
    )