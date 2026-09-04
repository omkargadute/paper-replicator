"""PDF document loader and layout-aware text extraction using PyMuPDF."""

import re
from pathlib import Path
from typing import List, Optional, Tuple
import fitz  # PyMuPDF

from paperrep.provenance.hasher import hash_file
from paperrep.schemas.paper import PaperDocument, PaperMetadata, PaperSection, PaperTable


class PDFLoader:
    """Extracts structured text, sections, metadata, and tables from scientific PDFs."""

    def __init__(self) -> None:
        self.url_regex = re.compile(
            r'https?://(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:/[^\s\)\]<>"\'\\]*)?'
        )

    def load(self, file_path: str | Path) -> PaperDocument:
        """Loads and parses a PDF into a structured PaperDocument.
        
        Args:
            file_path: Path to the research paper PDF.
            
        Returns:
            Structured PaperDocument with sections, metadata, tables, and file hash.
        """
        path = Path(file_path).resolve()
        if not path.is_file():
            raise FileNotFoundError(f"PDF file not found: {path}")

        file_hash = hash_file(path)
        doc = fitz.open(path)

        metadata = self._extract_metadata(doc, path.stem)
        sections, extracted_urls = self._extract_sections_and_urls(doc)
        tables = self._extract_tables(doc)

        return PaperDocument(
            file_path=str(path),
            file_hash_sha256=file_hash,
            metadata=metadata,
            sections=sections,
            tables=tables,
            extracted_urls=sorted(list(set(extracted_urls))),
        )

    def _extract_metadata(self, doc: fitz.Document, fallback_title: str) -> PaperMetadata:
        """Extracts bibliographic metadata from PDF properties and first page."""
        meta = doc.metadata or {}
        title = meta.get("title", "").strip() or fallback_title.replace("_", " ").title()
        author_str = meta.get("author", "").strip()
        authors = [a.strip() for a in re.split(r"[,;]", author_str) if a.strip()] if author_str else []

        # Inspect first page for title and abstract heuristics if metadata is sparse
        abstract = ""
        if len(doc) > 0:
            first_page_text = doc[0].get_text()
            abstract_match = re.search(r"(?i)\babstract\b[:\s]*(.+?)(?=\n\s*(?:1[\.\s]|introduction|keywords))", first_page_text, re.DOTALL)
            if abstract_match:
                abstract = re.sub(r"\s+", " ", abstract_match.group(1)).strip()

        return PaperMetadata(
            title=title,
            authors=authors,
            abstract=abstract,
        )

    def _extract_sections_and_urls(self, doc: fitz.Document) -> Tuple[List[PaperSection], List[str]]:
        """Extracts text, splits into sections based on headings, and extracts URLs."""
        all_urls: List[str] = []
        full_text_pages: List[Tuple[int, str]] = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            full_text_pages.append((page_num + 1, text))

            # Extract URLs from page text and links
            for match in self.url_regex.finditer(text):
                all_urls.append(match.group(0).rstrip(".,;"))

            for link in page.get_links():
                uri = link.get("uri")
                if uri and uri.startswith("http"):
                    all_urls.append(uri.rstrip(".,;"))

        # Chunk into sections using heading patterns
        sections: List[PaperSection] = []
        heading_pattern = re.compile(r"^(?:(\d+(?:\.\d+)*)\s+([A-Z][^\n]+)|([A-Z\s]{4,}))$", re.MULTILINE)

        current_title = "Abstract / Preamble"
        current_level = 1
        current_content_lines: List[str] = []

        for page_num, text in full_text_pages:
            lines = text.splitlines()
            for line in lines:
                clean_line = line.strip()
                if not clean_line:
                    continue

                heading_match = heading_pattern.match(clean_line)
                if heading_match and len(clean_line) < 80:
                    # Flush previous section
                    if current_content_lines:
                        sections.append(
                            PaperSection(
                                title=current_title,
                                level=current_level,
                                content="\n".join(current_content_lines),
                            )
                        )
                        current_content_lines = []

                    current_title = clean_line
                    current_level = 2 if "." in clean_line else 1
                else:
                    current_content_lines.append(clean_line)

        # Flush final section
        if current_content_lines:
            sections.append(
                PaperSection(
                    title=current_title,
                    level=current_level,
                    content="\n".join(current_content_lines),
                )
            )

        return sections, all_urls

    def _extract_tables(self, doc: fitz.Document) -> List[PaperTable]:
        """Extracts structured tables using PyMuPDF table detection."""
        extracted_tables: List[PaperTable] = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            try:
                # Use PyMuPDF's built-in table finder (available in PyMuPDF >= 1.23)
                tables = page.find_tables()
                for idx, tab in enumerate(tables):
                    df_data = tab.extract()
                    if not df_data or len(df_data) < 2:
                        continue

                    headers = [str(col).strip() if col is not None else "" for col in df_data[0]]
                    rows = [
                        [str(cell).strip() if cell is not None else "" for cell in row]
                        for row in df_data[1:]
                    ]

                    # Build markdown representation
                    md_lines = ["| " + " | ".join(headers) + " |"]
                    md_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
                    for row in rows:
                        md_lines.append("| " + " | ".join(row) + " |")
                    raw_markdown = "\n".join(md_lines)

                    extracted_tables.append(
                        PaperTable(
                            table_id=f"table_p{page_num + 1}_{idx + 1}",
                            caption=f"Table on page {page_num + 1}",
                            page_number=page_num + 1,
                            headers=headers,
                            rows=rows,
                            raw_markdown=raw_markdown,
                        )
                    )
            except Exception:
                # Graceful fallback if page has unusual layout
                continue

        return extracted_tables
