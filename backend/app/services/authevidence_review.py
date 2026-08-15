from pathlib import Path
from typing import Any

from app.evidence.extractor import extract_clinical_evidence
from app.evidence.matcher import match_evidence_to_criteria
from app.evidence.readiness import calculate_readiness
from app.retrieval.policy_loader import (
    find_policy_by_procedure_code,
    load_policy,
)


def _build_review_summary(
    readiness: dict[str, Any],
    policy: dict[str, Any],
) -> str:
    criteria_met = readiness.get("criteria_met", 0)
    criteria_total = readiness.get("criteria_total", 0)

    confidence = readiness.get("evidence_confidence", 0)
    confidence_level = readiness.get("confidence_level", "LOW")

    status = readiness.get("status", "INSUFFICIENT_DATA")

    missing = readiness.get("missing_evidence", [])

    if not missing:
        gap_text = "No documentation gaps were identified."
    else:
        gap_text = (
            f"{len(missing)} documentation gap(s) were identified."
        )

    if status == "READY_FOR_REVIEW":
        recommendation = (
            "The request is ready for reviewer assessment."
        )

    elif status == "NEARLY_READY":
        recommendation = (
            "The request is nearly ready, but additional "
            "documentation should be collected before final review."
        )

    elif status == "ADDITIONAL_DOCUMENTATION_REQUIRED":
        recommendation = (
            "Additional clinical documentation is required "
            "before the request is ready for review."
        )

    else:
        recommendation = (
            "The request does not currently contain enough "
            "supporting evidence for review."
        )

    return (
        f"{criteria_met} of {criteria_total} policy criteria were met. "
        f"Overall evidence confidence is {confidence}% "
        f"({confidence_level}). "
        f"{gap_text} "
        f"{recommendation}"
    )


def run_authevidence_review(
    patient_data: dict[str, Any],
    policy_path: str | Path | None = None,
    procedure_code: str | None = None,
    policy_directory: str | Path | None = None,
) -> dict[str, Any]:
    """
    Run the AuthEvidence AI prior-authorization review pipeline.
    """

    evidence = extract_clinical_evidence(patient_data)

    if policy_path is not None:
        policy = load_policy(policy_path)

    elif procedure_code and policy_directory:
        policy = find_policy_by_procedure_code(
            policy_directory=policy_directory,
            procedure_code=procedure_code,
        )

        if policy is None:
            raise ValueError(
                f"No policy found for procedure code: {procedure_code}"
            )

    else:
        raise ValueError(
            "Either policy_path or procedure_code + policy_directory "
            "must be provided."
        )

    criteria_results = match_evidence_to_criteria(
        evidence=evidence,
        policy=policy,
    )

    readiness = calculate_readiness(criteria_results)

    review_summary = _build_review_summary(
        readiness=readiness,
        policy=policy,
    )

    return {
        "patient_id": evidence.get("patient_id"),
        "policy": {
            "policy_id": policy.get("policy_id"),
            "title": policy.get("title"),
            "procedure_code": policy.get("procedure_code"),
            "procedure_name": policy.get("procedure_name"),
        },
        "clinical_evidence": evidence,
        "criteria_assessment": criteria_results,
        "authorization_readiness": readiness,
        "review_summary": review_summary,
    }