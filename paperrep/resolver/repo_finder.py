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
        # 1. Search in extracted URLs
        for url in paper.extracted_urls:
            cleaned_url = self._clean_repo_url(url)
            if cleaned_url:
                return cleaned_url

        # 2. Search in raw section texts (e.g. footnotes or code availability statement)
        for sec in paper.sections:
            if any(term in sec.title.lower() for term in ["code", "availability", "reproducibility", "implementation"]):
                match = self.GITHUB_PATTERN.search(sec.content)
                if match:
                    return f"https://github.com/{match.group(1).rstrip('.')}"

        # 3. Fallback: Search anywhere in document
        for sec in paper.sections:
            match = self.GITHUB_PATTERN.search(sec.content)
            if match:
                return f"https://github.com/{match.group(1).rstrip('.')}"

        return None

    def _clean_repo_url(self, url: str) -> Optional[str]:
        """Validates and normalizes git repository URLs."""
        match = self.GITHUB_PATTERN.match(url)
        if match:
            repo_path = match.group(1).rstrip(".git").rstrip(".")
            # Filter out non-code pages or common generic GitHub URLs
            if not any(repo_path.startswith(prefix) for prefix in ["features/", "pricing/", "about/", "join/"]):
                return f"https://github.com/{repo_path}"

        match_gl = self.GITLAB_PATTERN.match(url)
        if match_gl:
            return f"https://gitlab.com/{match_gl.group(1).rstrip('.')}"

        return None
