"""Experiment plan synthesis from extracted claims and paper specifications."""

from typing import Optional
from paperrep.schemas.claim import ClaimSpec
from paperrep.schemas.experiment import DatasetSpec, ExperimentPlan, HardwareProfile
from paperrep.schemas.paper import PaperDocument


class SpecGenerator:
    """Generates executable ExperimentPlan contracts from extracted scientific claims."""

    @staticmethod
    def generate_plan(
        claim: ClaimSpec,
        paper: PaperDocument,
        repo_url: Optional[str] = None,
        repo_commit: Optional[str] = None,
        gpu_required: bool = False,
        timeout_seconds: int = 1800,
    ) -> ExperimentPlan:
        """Constructs an ExperimentPlan binding the claim, resolved assets, and execution contract.
        
        Args:
            claim: Verifiable claim specification.
            paper: Structured paper document.
            repo_url: Resolved git repository URL if found.
            repo_commit: Pinned git commit SHA.
            gpu_required: Whether to enforce GPU allocation.
            timeout_seconds: Hard execution watchdog timeout.
            
        Returns:
            Validated ExperimentPlan object.
        """
        # Determine dataset source
        dataset_source_type = "huggingface"
        dataset_uri = claim.dataset_name.lower().replace(" ", "-")

        # Check if torchvision dataset
        if any(ds in claim.dataset_name.lower() for ds in ["cifar", "mnist", "imagenet", "fashion"]):
            dataset_source_type = "torchvision"
            dataset_uri = f"torchvision.datasets.{claim.dataset_name.upper()}"

        dataset_spec = DatasetSpec(
            name=claim.dataset_name,
            source_type=dataset_source_type,
            source_uri=dataset_uri,
            split=claim.dataset_split,
        )

        hardware_profile = HardwareProfile(
            gpu_required=gpu_required,
            min_vram_gb=4.0 if gpu_required else 0.0,
            cpu_cores=4,
            memory_limit="8g",
            timeout_seconds=timeout_seconds,
        )

        entry_point = "python paperrep_harness.py"

        return ExperimentPlan(
            experiment_id=f"EXP_{claim.claim_id}",
            target_claim_id=claim.claim_id,
            repo_url=repo_url,
            repo_commit=repo_commit,
            dataset=dataset_spec,
            entry_point_command=entry_point,
            hyperparameters={"seed": 42, "batch_size": 32},
            seeds=[42],
            hardware=hardware_profile,
            expected_metrics_output_path="/workspace/output/reproduce_metrics.json",
        )
