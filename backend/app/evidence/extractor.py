from typing import Any


def extract_clinical_evidence(patient_data: dict[str, Any]) -> dict[str, Any]:
    """
    Normalize patient/FHIR-style clinical data into evidence that can be
    consumed by the prior-authorization review workflow.
    """

    evidence = {
        "patient_id": patient_data.get("patient_id"),
        "age": patient_data.get("age"),
        "gender": patient_data.get("gender"),
        "diagnoses": [],
        "medications": [],
        "procedures": [],
        "observations": [],
        "encounters": [],
        "supporting_evidence": [],
    }

    # Diagnoses
    for diagnosis in patient_data.get("conditions", []):
        item = {
            "code": diagnosis.get("code"),
            "description": diagnosis.get("description"),
            "onset_date": diagnosis.get("onset_date"),
            "status": diagnosis.get("status"),
        }

        evidence["diagnoses"].append(item)

        if diagnosis.get("description"):
            evidence["supporting_evidence"].append(
                f"Diagnosis: {diagnosis['description']}"
            )

    # Medications
    for medication in patient_data.get("medications", []):
        item = {
            "name": medication.get("name"),
            "status": medication.get("status"),
            "start_date": medication.get("start_date"),
            "duration_weeks": medication.get("duration_weeks"),
        }

        evidence["medications"].append(item)

        if medication.get("name"):
            description = f"Medication: {medication['name']}"

            if medication.get("duration_weeks"):
                description += (
                    f" for {medication['duration_weeks']} weeks"
                )

            evidence["supporting_evidence"].append(description)

    # Procedures
    for procedure in patient_data.get("procedures", []):
        item = {
            "code": procedure.get("code"),
            "description": procedure.get("description"),
            "date": procedure.get("date"),
        }

        evidence["procedures"].append(item)

        if procedure.get("description"):
            evidence["supporting_evidence"].append(
                f"Procedure: {procedure['description']}"
            )

    # Clinical observations
    for observation in patient_data.get("observations", []):
        item = {
            "name": observation.get("name"),
            "value": observation.get("value"),
            "unit": observation.get("unit"),
            "date": observation.get("date"),
        }

        evidence["observations"].append(item)

        if observation.get("name"):
            value = observation.get("value", "")
            unit = observation.get("unit", "")

            evidence["supporting_evidence"].append(
                f"Observation: {observation['name']} = {value} {unit}".strip()
            )

    # Encounters
    for encounter in patient_data.get("encounters", []):
        item = {
            "type": encounter.get("type"),
            "date": encounter.get("date"),
            "reason": encounter.get("reason"),
        }

        evidence["encounters"].append(item)

        if encounter.get("reason"):
            evidence["supporting_evidence"].append(
                f"Encounter: {encounter['reason']}"
            )

    return evidence