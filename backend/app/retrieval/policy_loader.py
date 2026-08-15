import json
from pathlib import Path
from typing import Any


def load_policy(file_path: str | Path) -> dict[str, Any]:
    """
    Load a prior-authorization policy from a JSON file.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Policy file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        policy = json.load(file)

    required_fields = {
        "policy_id",
        "title",
        "policy_type",
        "procedure_code",
        "procedure_name",
        "criteria",
    }

    missing_fields = required_fields - policy.keys()

    if missing_fields:
        raise ValueError(
            f"Policy is missing required fields: {sorted(missing_fields)}"
        )

    if not isinstance(policy["criteria"], list):
        raise ValueError("Policy criteria must be a list")

    return policy


def get_policy_criteria(policy: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Return the coverage criteria from a loaded policy.
    """
    return policy.get("criteria", [])

def find_policy_by_procedure_code(
    policy_directory: str | Path,
    procedure_code: str,
) -> dict[str, Any] | None:
    """
    Search all JSON policy files in a directory and return the first
    policy whose procedure_code matches the requested code.
    """

    directory = Path(policy_directory)

    if not directory.exists():
        raise FileNotFoundError(
            f"Policy directory not found: {directory}"
        )

    for policy_file in directory.glob("*.json"):
        policy = load_policy(policy_file)

        if str(policy.get("procedure_code")) == str(procedure_code):
            return policy

    return None