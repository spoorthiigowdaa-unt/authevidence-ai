from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.evidence.fhir_parser import parse_fhir_bundle
from app.services.authevidence_review import run_authevidence_review
from app.services.coverage_enrichment import enrich_with_coverage_agent


router = APIRouter(
    prefix="/authevidence",
    tags=["AuthEvidence AI"],
)


class PriorAuthorizationRequest(BaseModel):
    patient_data: dict[str, Any] | None = None
    fhir_bundle: dict[str, Any] | None = None
    procedure_code: str
    provider_npi: str | None = None
    use_coverage_agent: bool = False


@router.post("/review")
async def review_prior_authorization(
    request: PriorAuthorizationRequest,
):
    """
    Run an AuthEvidence AI prior-authorization review.

    Supports:
    - Standard patient JSON
    - FHIR R4 Bundle input
    - Procedure-based policy selection
    - Optional provider NPI
    - Optional CMS/NPI Coverage Agent enrichment
    """

    project_root = Path(__file__).resolve().parents[3]

    policy_directory = (
        project_root
        / "policies"
        / "sample"
    )

    # ---------------------------------------------------------
    # 1. Determine input format
    # ---------------------------------------------------------

    if request.fhir_bundle is not None:
        patient_data = parse_fhir_bundle(
            request.fhir_bundle
        )

    elif request.patient_data is not None:
        patient_data = request.patient_data

    else:
        raise HTTPException(
            status_code=422,
            detail=(
                "Provide either patient_data "
                "or fhir_bundle."
            ),
        )

    # ---------------------------------------------------------
    # 2. Run local AuthEvidence review
    # ---------------------------------------------------------

    try:
        result = run_authevidence_review(
            patient_data=patient_data,
            procedure_code=request.procedure_code,
            policy_directory=policy_directory,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    # ---------------------------------------------------------
    # 3. Optional Coverage Agent enrichment
    # ---------------------------------------------------------

    if request.use_coverage_agent:

        coverage_request = {
            "provider_npi": request.provider_npi,
            "procedure_codes": [
                request.procedure_code
            ],
            "diagnosis_codes": [
                diagnosis.get("code")
                for diagnosis in result[
                    "clinical_evidence"
                ].get("diagnoses", [])
                if diagnosis.get("code")
            ],
            "patient": {
                "patient_id": result.get(
                    "patient_id"
                ),
            },
        }

        clinical_findings = {
            "clinical_extraction": result.get(
                "clinical_evidence",
                {},
            ),
            "criteria_assessment": result.get(
                "criteria_assessment",
                [],
            ),
        }

        coverage_enrichment = (
            await enrich_with_coverage_agent(
                request_data=coverage_request,
                clinical_findings=clinical_findings,
            )
        )

        result["coverage_enrichment"] = (
            coverage_enrichment
        )

    else:
        result["coverage_enrichment"] = {
            "available": False,
            "reason": (
                "Coverage Agent enrichment "
                "was not requested."
            ),
        }

    return result