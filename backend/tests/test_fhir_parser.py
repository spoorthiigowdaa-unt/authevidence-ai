from app.evidence.fhir_parser import parse_fhir_bundle


def test_parse_fhir_bundle():
    bundle = {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": "PAT-3001",
                    "gender": "female",
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "clinicalStatus": {
                        "coding": [
                            {
                                "code": "active"
                            }
                        ]
                    },
                    "code": {
                        "coding": [
                            {
                                "code": "M54.16",
                                "display": "Lumbar radiculopathy",
                            }
                        ]
                    },
                    "onsetDateTime": "2026-06-01",
                }
            },
            {
                "resource": {
                    "resourceType": "MedicationRequest",
                    "status": "completed",
                    "medicationCodeableConcept": {
                        "coding": [
                            {
                                "display": "Naproxen"
                            }
                        ]
                    },
                    "authoredOn": "2026-06-10",
                }
            },
            {
                "resource": {
                    "resourceType": "Procedure",
                    "code": {
                        "coding": [
                            {
                                "code": "97110",
                                "display": "Physical therapy",
                            }
                        ]
                    },
                    "performedDateTime": "2026-07-01",
                }
            },
            {
                "resource": {
                    "resourceType": "Observation",
                    "code": {
                        "coding": [
                            {
                                "display": "Pain score"
                            }
                        ]
                    },
                    "valueQuantity": {
                        "value": 8,
                        "unit": "/10",
                    },
                    "effectiveDateTime": "2026-07-20",
                }
            },
            {
                "resource": {
                    "resourceType": "Encounter",
                    "class": {
                        "display": "Outpatient"
                    },
                    "period": {
                        "start": "2026-07-20"
                    },
                    "reasonCode": [
                        {
                            "coding": [
                                {
                                    "display": "Persistent lower-back pain"
                                }
                            ]
                        }
                    ],
                }
            },
        ],
    }

    result = parse_fhir_bundle(bundle)

    assert result["patient_id"] == "PAT-3001"
    assert result["gender"] == "female"

    assert len(result["conditions"]) == 1
    assert result["conditions"][0]["code"] == "M54.16"

    assert len(result["medications"]) == 1
    assert result["medications"][0]["name"] == "Naproxen"

    assert len(result["procedures"]) == 1
    assert result["procedures"][0]["description"] == "Physical therapy"

    assert len(result["observations"]) == 1
    assert result["observations"][0]["value"] == 8

    assert len(result["encounters"]) == 1
    assert (
        result["encounters"][0]["reason"]
        == "Persistent lower-back pain"
    )