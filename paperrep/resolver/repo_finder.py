"""Repository and open-source code discovery engine."""

import re
from typing import List, Optional
from paperrep.schemas.paper import PaperDocument


class RepoFinder:
    """Discovers official GitHub, GitLab, and Zenodo code repositories from research papers."""

    GITHUB_PATTERN = re.compile(r'https?://github\.com/([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)')
    GITLAB_PATTERN = re.compile(r'https?://gitlab\.com/([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)')
    ZENODO_PATTERN = re.compile(r'https?://zenodo\.org/record/([0-9]+)')

    def find_repository(self, paper: PaperDocument) -> Optional[str]:
        """Scans extracted URLs and paper text for official repository links.
        
        Args:
            paper: Structured paper document.
            
        Returns:
            Normalized repository URL if found, else None.
        """
        candidate_repos: List[str] = []

        # 1. Inspect extracted URLs
        for url in paper.extracted_urls:
            cleaned_url = self._clean_repo_url(url)
            if cleaned_url and cleaned_url not in candidate_repos:
                candidate_repos.append(cleaned_url)

        # 2. Inspect section texts near code availability keywords
        for sec in paper.sections:
            if any(term in sec.title.lower() for term in ["code", "availability", "reproducibility", "implementation", "introduction"]):
                for match in self.GITHUB_PATTERN.finditer(sec.content):
                    cleaned = self._clean_repo_url(match.group(0))
                    if cleaned and cleaned not in candidate_repos:
                        candidate_repos.insert(0, cleaned)

        if not candidate_repos:
            return None

        # Prioritize core model/framework repos over peripheral repos
        # E.g. huggingface/transformers > swift-coreml-transformers
        for repo in candidate_repos:
            repo_lower = repo.lower()
            if any(core in repo_lower for core in ["transformers", "models", "torchvision", "detectron", "fairseq"]):
                return repo

        return candidate_repos[0]

    def _clean_repo_url(self, url: str) -> Optional[str]:
        """Validates and normalizes git repository URLs."""
        match = self.GITHUB_PATTERN.match(url)
        if match:
            repo_path = match.group(1).rstrip(".git").rstrip(".")
            if not any(repo_path.startswith(prefix) for prefix in ["features/", "pricing/", "about/", "join/"]):
                return f"https://github.com/{repo_path}"

        match_gl = self.GITLAB_PATTERN.match(url)
        if match_gl:
            return f"https://gitlab.com/{match_gl.group(1).rstrip('.')}"

        return None
