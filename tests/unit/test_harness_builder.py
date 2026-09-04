"""Unit tests for HarnessBuilder and syntax validation."""

import ast
from paperrep.schemas.claim import CitationCoordinate, ClaimSpec, ClaimType
from paperrep.schemas.experiment import DatasetSpec, ExperimentPlan, HardwareProfile
from paperrep.synthesis.harness_builder import HarnessBuilder
from paperrep.synthesis.iterative_repair import HarnessRepairEngine


def test_harness_builder_generates_valid_syntax():
    claim = ClaimSpec(
        claim_id="CLM_TEST",
        statement="Model achieves 91.4% accuracy",
        claim_type=ClaimType.VERIFIABLE_NUMERIC,
        metric_name="Accuracy",
        published_value=91.4,
        dataset_name="CIFAR-10",
        model_name="ResNet",
        citation=CitationCoordinate(page_number=1),
    )
    plan = ExperimentPlan(
        experiment_id="EXP_TEST",
        target_claim_id="CLM_TEST",
        dataset=DatasetSpec(name="CIFAR-10", source_type="torchvision", source_uri="CIFAR10"),
        entry_point_command="python eval.py",
        seeds=[42],
        expected_metrics_output_path="/tmp/metrics.json",
    )

    builder = HarnessBuilder()
    code = builder.build_harness_script(plan, claim)
    assert "reproduce_metrics.json" not in code or "/tmp/metrics.json" in code
    assert "SEED = 42" in code

    # Validate AST
    is_valid, err = HarnessRepairEngine.validate_syntax(code)
    assert is_valid is True
    assert err == ""


def test_repair_engine_catches_syntax_error():
    broken_code = "def foo(: print('broken')"
    is_valid, err = HarnessRepairEngine.validate_syntax(broken_code)
    assert is_valid is False
    assert "SyntaxError" in err


def test_patch_common_deprecations():
    old_code = "val = np.float(3.14) + np.int(5)"
    patched = HarnessRepairEngine.patch_common_deprecations(old_code)
    assert "np.float" not in patched
    assert "np.int" not in patched
