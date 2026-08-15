from typing import Any


def parse_fhir_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    """
    Convert a simplified FHIR R4 Bundle into the patient_data structure
    used by AuthEvidence AI.
    """

    patient_data = {
        "patient_id": None,
        "age": None,
        "gender": None,
        "conditions": [],
        "medications": [],
        "procedures": [],
        "observations": [],
        "encounters": [],
    }

    for entry in bundle.get("entry", []):
        resource = entry.get("resource", {})
        resource_type = resource.get("resourceType")

        if resource_type == "Patient":
            patient_data["patient_id"] = resource.get("id")
            patient_data["gender"] = resource.get("gender")

        elif resource_type == "Condition":
            coding = (
                resource.get("code", {})
                .get("coding", [{}])[0]
            )

            patient_data["conditions"].append(
                {
                    "code": coding.get("code"),
                    "description": coding.get("display"),
                    "status": (
                        resource.get("clinicalStatus", {})
                        .get("coding", [{}])[0]
                        .get("code")
                    ),
                    "onset_date": resource.get("onsetDateTime"),
                }
            )

        elif resource_type == "MedicationRequest":
            coding = (
                resource.get("medicationCodeableConcept", {})
                .get("coding", [{}])[0]
            )

            patient_data["medications"].append(
                {
                    "name": coding.get("display"),
                    "status": resource.get("status"),
                    "start_date": (
                        resource.get("authoredOn")
                    ),
                    "duration_weeks": None,
                }
            )

        elif resource_type == "Procedure":
            coding = (
                resource.get("code", {})
                .get("coding", [{}])[0]
            )

            patient_data["procedures"].append(
                {
                    "code": coding.get("code"),
                    "description": coding.get("display"),
                    "date": resource.get("performedDateTime"),
                }
            )

        elif resource_type == "Observation":
            coding = (
                resource.get("code", {})
                .get("coding", [{}])[0]
            )

            quantity = resource.get("valueQuantity", {})

            patient_data["observations"].append(
                {
                    "name": coding.get("display"),
                    "value": quantity.get("value"),
                    "unit": quantity.get("unit"),
                    "date": resource.get("effectiveDateTime"),
                }
            )

        elif resource_type == "Encounter":
            reason = ""

            reason_list = resource.get("reasonCode", [])

            if reason_list:
                reason_coding = (
                    reason_list[0]
                    .get("coding", [{}])[0]
                )
                reason = reason_coding.get("display", "")

            patient_data["encounters"].append(
                {
                    "type": (
                        resource.get("class", {})
                        .get("display")
                    ),
                    "date": (
                        resource.get("period", {})
                        .get("start")
                    ),
                    "reason": reason,
                }
            )

    return patient_data