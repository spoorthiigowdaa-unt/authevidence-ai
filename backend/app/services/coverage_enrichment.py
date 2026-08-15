from typing import Any

from app.agents.coverage_agent import run_coverage_review


async def enrich_with_coverage_agent(
    request_data: dict[str, Any],
    clinical_findings: dict[str, Any],
) -> dict[str, Any]:
    """
    Run the existing Coverage Assessment Agent when available.

    If the hosted agent cannot be reached locally, return a safe
    unavailable result without breaking the AuthEvidence pipeline.
    """

    try:
        result = await run_coverage_review(
            request_data=request_data,
            clinical_findings=clinical_findings,
        )

        return {
            "available": True,
            "provider_verification": result.get(
                "provider_verification"
            ),
            "coverage_policies": result.get(
                "coverage_policies",
                [],
            ),
            "policy_references": result.get(
                "policy_references",
                [],
            ),
            "coverage_limitations": result.get(
                "coverage_limitations",
                [],
            ),
            "documentation_gaps": result.get(
                "documentation_gaps",
                [],
            ),
            "tool_results": result.get(
                "tool_results",
                [],
            ),
        }

    except Exception as exc:
        return {
            "available": False,
            "provider_verification": None,
            "coverage_policies": [],
            "policy_references": [],
            "coverage_limitations": [],
            "documentation_gaps": [],
            "tool_results": [
                {
                    "tool_name": "coverage_agent",
                    "status": "warning",
                    "detail": (
                        "External Coverage Agent unavailable: "
                        f"{exc}"
                    ),
                }
            ],
        }