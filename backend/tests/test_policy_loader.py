from pathlib import Path

from app.retrieval.policy_loader import get_policy_criteria, load_policy
from app.retrieval.policy_loader import (
    find_policy_by_procedure_code,
)


def test_load_policy():
    project_root = Path(__file__).resolve().parents[2]

    policy_path = (
        project_root
        / "policies"
        / "sample"
        / "lumbar_mri_policy.json"
    )

    policy = load_policy(policy_path)

    assert policy["policy_id"] == "SAMPLE-LUMBAR-MRI-001"
    assert policy["procedure_code"] == "72148"
    assert policy["procedure_name"] == "MRI Lumbar Spine Without Contrast"

    criteria = get_policy_criteria(policy)

    assert len(criteria) == 4
    assert criteria[0]["id"] == "C1"



def test_find_policy_by_procedure_code():
    project_root = Path(__file__).resolve().parents[2]

    policy_directory = (
        project_root
        / "policies"
        / "sample"
    )

    policy = find_policy_by_procedure_code(
        policy_directory=policy_directory,
        procedure_code="72148",
    )

    assert policy is not None
    assert policy["policy_id"] == "SAMPLE-LUMBAR-MRI-001"
    assert policy["procedure_code"] == "72148"