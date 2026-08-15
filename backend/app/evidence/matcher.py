from typing import Any


def _normalize(text: str) -> str:
    return str(text or "").lower().strip()


def _collect_evidence_text(evidence: dict[str, Any]) -> list[str]:
    texts = []

    for diagnosis in evidence.get("diagnoses", []):
        texts.append(
            f"diagnosis {_normalize(diagnosis.get('description'))}"
        )

    for medication in evidence.get("medications", []):
        name = _normalize(medication.get("name"))
        duration = medication.get("duration_weeks")

        text = f"medication {name}"

        if duration is not None:
            text += f" {duration} weeks"

        texts.append(text)

    for procedure in evidence.get("procedures", []):
        texts.append(
            f"procedure {_normalize(procedure.get('description'))}"
        )

    for observation in evidence.get("observations", []):
        texts.append(
            f"observation {_normalize(observation.get('name'))} "
            f"{_normalize(observation.get('value'))}"
        )

    for encounter in evidence.get("encounters", []):
        texts.append(
            f"encounter {_normalize(encounter.get('reason'))}"
        )

    return texts


def _criterion_keywords(criterion: dict[str, Any]) -> list[str]:
    """
    Use explicit keywords when available.
    Falls back to important words from the criterion description.
    """

    keywords = criterion.get("keywords")

    if keywords:
        return [_normalize(keyword) for keyword in keywords]

    description = _normalize(criterion.get("description"))

    stop_words = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "of",
        "for",
        "to",
        "has",
        "been",
        "is",
        "are",
        "with",
        "at",
        "least",
        "supporting",
        "documented",
    }

    return [
        word
        for word in description.replace("-", " ").split()
        if len(word) >= 4 and word not in stop_words
    ]


def match_evidence_to_criteria(
    evidence: dict[str, Any],
    policy: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Generic evidence-to-policy matcher.

    Matches policy-defined keywords against normalized clinical evidence.
    """

    evidence_texts = _collect_evidence_text(evidence)

    results = []

    for criterion in policy.get("criteria", []):
        criterion_id = criterion.get("id")
        description = criterion.get("description", "")

        keywords = _criterion_keywords(criterion)

        matched_evidence = []

        for evidence_text in evidence_texts:
            if any(
                keyword in evidence_text
                for keyword in keywords
            ):
                matched_evidence.append(evidence_text)

        if matched_evidence:
            status = "MET"

            keyword_hits = sum(
                1
                for keyword in keywords
                if any(
                    keyword in evidence_text
                    for evidence_text in evidence_texts
                )
            )

            coverage_ratio = (
                keyword_hits / len(keywords)
                if keywords
                else 0
            )

            confidence = min(
                98,
                round(70 + (coverage_ratio * 28)),
            )

            notes = (
                "Clinical evidence matched the policy criterion."
            )

        else:
            status = "INSUFFICIENT"
            confidence = 25
            notes = (
                "No sufficient supporting clinical evidence was found."
            )

        results.append(
            {
                "criterion_id": criterion_id,
                "criterion": description,
                "status": status,
                "confidence": confidence,
                "met": status == "MET",
                "evidence": matched_evidence,
                "notes": notes,
                "source": policy.get("policy_id"),
            }
        )

    return results