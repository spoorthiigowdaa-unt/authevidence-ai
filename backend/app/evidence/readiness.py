from typing import Any


def calculate_readiness(
    criteria_results: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Calculate authorization readiness, overall evidence confidence,
    and identify missing evidence.
    """

    total = len(criteria_results)

    if total == 0:
        return {
            "readiness_score": 0,
            "evidence_confidence": 0,
            "confidence_level": "LOW",
            "criteria_met": 0,
            "criteria_total": 0,
            "missing_evidence": [],
            "status": "INSUFFICIENT_DATA",
        }

    met_count = sum(
        1
        for item in criteria_results
        if item.get("status") == "MET"
    )

    readiness_score = round((met_count / total) * 100)

    confidence_values = [
        item.get("confidence", 0)
        for item in criteria_results
        if isinstance(item.get("confidence"), (int, float))
    ]

    evidence_confidence = round(
        sum(confidence_values) / len(confidence_values),
        2,
    ) if confidence_values else 0

    if evidence_confidence >= 85:
        confidence_level = "HIGH"
    elif evidence_confidence >= 60:
        confidence_level = "MEDIUM"
    else:
        confidence_level = "LOW"

    missing_evidence = []

    for item in criteria_results:
        if item.get("status") != "MET":

            criterion_id = item.get("criterion_id")
            criterion_text = item.get("criterion", "")

            request_text = (
                f"Please provide documentation supporting: {criterion_text}"
            )

            if criterion_id == "C1":
                request_text = (
                    "Please provide documentation showing that the patient's "
                    "lower-back symptoms have persisted for at least 6 weeks."
                )

            elif criterion_id == "C2":
                request_text = (
                    "Please provide documentation of conservative medication "
                    "therapy that has been attempted."
                )

            elif criterion_id == "C3":
                request_text = (
                    "Please provide documentation of physical therapy "
                    "or another conservative treatment attempt."
                )

            elif criterion_id == "C4":
                request_text = (
                    "Please provide documentation of a relevant clinical "
                    "diagnosis supporting lumbar imaging."
                )

            missing_evidence.append(
                {
                    "criterion_id": criterion_id,
                    "criterion": criterion_text,
                    "status": item.get("status"),
                    "reason": item.get(
                        "notes",
                        "Supporting clinical evidence is missing.",
                    ),
                    "request": request_text,
                }
            )

    if readiness_score == 100:
        status = "READY_FOR_REVIEW"

    elif readiness_score >= 75:
        status = "NEARLY_READY"

    elif readiness_score >= 50:
        status = "ADDITIONAL_DOCUMENTATION_REQUIRED"

    else:
        status = "NOT_READY"

    return {
        "readiness_score": readiness_score,
        "evidence_confidence": evidence_confidence,
        "confidence_level": confidence_level,
        "criteria_met": met_count,
        "criteria_total": total,
        "missing_evidence": missing_evidence,
        "status": status,
    }