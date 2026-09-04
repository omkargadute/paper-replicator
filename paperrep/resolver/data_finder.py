"""Dataset resolution and public repository locator."""

from typing import Optional
from paperrep.schemas.experiment import DatasetSpec


class DataFinder:
    """Resolves scientific dataset names to public download sources (Hugging Face, Torchvision, direct URLs)."""

    TORCHVISION_DATASETS = {
        "cifar-10": "torchvision.datasets.CIFAR10",
        "cifar-100": "torchvision.datasets.CIFAR100",
        "mnist": "torchvision.datasets.MNIST",
        "fashion-mnist": "torchvision.datasets.FashionMNIST",
        "svhn": "torchvision.datasets.SVHN",
    }

    HUGGINGFACE_CANONICAL = {
        "sst-2": "glue/sst2",
        "sst2": "glue/sst2",
        "mrpc": "glue/mrpc",
        "qnli": "glue/qnli",
        "qqp": "glue/qqp",
        "squad": "squad",
        "imdb": "imdb",
        "ag_news": "ag_news",
        "wmt14": "wmt14",
    }

    def resolve(self, dataset_name: str, split: str = "test") -> DatasetSpec:
        """Resolves dataset name to a validated DatasetSpec."""
        norm_name = dataset_name.lower().strip().replace(" ", "-").replace("_", "-")

        # Check Torchvision
        if norm_name in self.TORCHVISION_DATASETS:
            return DatasetSpec(
                name=dataset_name,
                source_type="torchvision",
                source_uri=self.TORCHVISION_DATASETS[norm_name],
                split=split,
            )

        # Check Hugging Face canonical mapping
        if norm_name in self.HUGGINGFACE_CANONICAL:
            return DatasetSpec(
                name=dataset_name,
                source_type="huggingface",
                source_uri=self.HUGGINGFACE_CANONICAL[norm_name],
                split=split,
            )

        # Default fallback to Hugging Face Hub search identifier
        return DatasetSpec(
            name=dataset_name,
            source_type="huggingface",
            source_uri=norm_name,
            split=split,
        )
