"""Paper document schemas and metadata definitions."""

from typing import Dict, List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class CitationCoordinate(BaseModel):
    """Pinpoints the exact location of a claim or table within a paper."""
    page_number: int = Field(..., description="1-indexed page number in the PDF")
    section_title: Optional[str] = Field(None, description="Section heading (e.g. '5.2 Evaluation')")
    paragraph_index: Optional[int] = Field(None, description="Paragraph offset in section")
    table_identifier: Optional[str] = Field(None, description="Table identifier (e.g. 'Table 1')")
    table_row: Optional[str] = Field(None, description="Target row name/index")
    table_column: Optional[str] = Field(None, description="Target column metric header")


class PaperTable(BaseModel):
    """Structured representation of an extracted table."""
    table_id: str = Field(..., description="Table identifier, e.g. 'table_1'")
    caption: str = Field("", description="Table caption text")
    page_number: int = Field(..., description="Page number where table appears")
    headers: List[str] = Field(default_factory=list, description="Column headers")
    rows: List[List[str]] = Field(default_factory=list, description="Row cell contents")
    raw_markdown: str = Field("", description="Markdown formatted table")


class PaperSection(BaseModel):
    """A logical section within a parsed paper."""
    title: str = Field(..., description="Section title or heading")
    level: int = Field(1, description="Header level (1 for #, 2 for ##, etc.)")
    content: str = Field(..., description="Clean markdown content of section")


class PaperMetadata(BaseModel):
    """Bibliographic metadata extracted from paper."""
    title: str = Field(..., description="Title of the paper")
    authors: List[str] = Field(default_factory=list, description="List of author names")
    year: Optional[int] = Field(None, description="Publication year")
    arxiv_id: Optional[str] = Field(None, description="arXiv ID if applicable")
    doi: Optional[str] = Field(None, description="DOI if applicable")
    abstract: str = Field("", description="Abstract text")


class PaperDocument(BaseModel):
    """Complete structured representation of an ingested scientific paper."""
    paper_id: UUID = Field(default_factory=uuid4, description="Unique internal paper UUID")
    file_path: str = Field(..., description="Original PDF file path")
    file_hash_sha256: str = Field(..., description="Cryptographic SHA-256 hash of PDF")
    metadata: PaperMetadata = Field(..., description="Bibliographic metadata")
    sections: List[PaperSection] = Field(default_factory=list, description="Parsed text sections")
    tables: List[PaperTable] = Field(default_factory=list, description="Extracted tables")
    extracted_urls: List[str] = Field(default_factory=list, description="URLs found in text and footnotes")
