"""Reproducibility report compiler rendering Markdown and standalone HTML."""

from pathlib import Path
from typing import Tuple
from jinja2 import Environment, FileSystemLoader

from paperrep.schemas.report import ReproducibilityReport


class ReportGenerator:
    """Renders ReproducibilityReport instances into GitHub-flavored Markdown and HTML."""

    def __init__(self, templates_dir: Path | str | None = None) -> None:
        if templates_dir is None:
            self.templates_dir = Path(__file__).parent / "templates"
        else:
            self.templates_dir = Path(templates_dir)

        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render_markdown(self, report: ReproducibilityReport) -> str:
        """Renders report into GitHub-flavored Markdown."""
        template = self.env.get_template("report_markdown.j2")
        return template.render(report=report)

    def render_html(self, report: ReproducibilityReport) -> str:
        """Renders report into standalone HTML dashboard."""
        template = self.env.get_template("report_html.j2")
        return template.render(report=report)

    def save_reports(
        self,
        report: ReproducibilityReport,
        output_dir: Path | str,
        base_filename: str = "reproducibility_report",
    ) -> Tuple[Path, Path]:
        """Saves both Markdown and HTML reports to disk.
        
        Returns:
            Tuple of (markdown_file_path, html_file_path)
        """
        out_path = Path(output_dir).resolve()
        out_path.mkdir(parents=True, exist_ok=True)

        md_content = self.render_markdown(report)
        md_file = out_path / f"{base_filename}.md"
        md_file.write_text(md_content, encoding="utf-8")

        html_content = self.render_html(report)
        html_file = out_path / f"{base_filename}.html"
        html_file.write_text(html_content, encoding="utf-8")

        return md_file, html_file
