from app.evidence.extractor import extract_clinical_evidence


def test_extract_clinical_evidence():
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

    result = extract_clinical_evidence(patient)

    assert result["patient_id"] == "PAT-1001"
    assert len(result["diagnoses"]) == 1
    assert len(result["medications"]) == 1
    assert len(result["procedures"]) == 1
    assert len(result["observations"]) == 1
    assert len(result["encounters"]) == 1

    assert "Diagnosis: Lumbar radiculopathy" in result["supporting_evidence"]
    assert "Medication: Naproxen for 6 weeks" in result["supporting_evidence"]