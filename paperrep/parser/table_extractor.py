"""Specialized scientific table extractor and numerical claim locator."""

import re
from typing import Dict, List, Optional, Tuple
from paperrep.schemas.paper import PaperTable


class TableExtractor:
    """Parses scientific benchmark tables to locate candidate numeric claims."""

    @staticmethod
    def extract_text_tables(page_text: str, page_number: int) -> List[PaperTable]:
        """Extracts borderless LaTeX text tables from scientific paper pages."""
        tables: List[PaperTable] = []
        tab_matches = list(re.finditer(r'(?i)\bTable\s+(\d+)[:\.]?\s*([^\n]*)', page_text))
        
        for i, m in enumerate(tab_matches):
            tab_num = m.group(1)
            caption = m.group(0).strip()
            start = m.start()
            end = tab_matches[i + 1].start() if i + 1 < len(tab_matches) else min(len(page_text), start + 1500)
            block = page_text[start:end]
            lines = [l.strip() for l in block.splitlines() if l.strip()]

            rows: List[List[str]] = []
            
            # Strategy A: Check for line-adjacent model names and numbers
            for idx in range(len(lines) - 1):
                l1 = lines[idx]
                l2 = lines[idx + 1]
                is_model = any(k in l1.lower() for k in [
                    'bert', 'distilbert', 'elmo', 'roberta', 'resnet', 'transformer',
                    'ours', 'baseline', 'model', 'student', 'teacher'
                ])
                if is_model:
                    num_m = re.match(r'^([0-9]{2}(?:\.[0-9]+)?)$', l2)
                    if num_m:
                        rows.append([l1, num_m.group(1)])

            # Strategy B: Check for single line formatted rows (e.g. "DistilBERT  92.82")
            if not rows:
                for line in lines:
                    single_m = re.match(r'^([A-Za-z0-9_.-]+(?:\s+[A-Za-z0-9_.-]+)?)\s+([0-9]{2}(?:\.[0-9]+)?)$', line)
                    if single_m:
                        rows.append([single_m.group(1), single_m.group(2)])

            if rows:
                headers = ["Model", "Metric Score"]
                md_lines = ["| " + " | ".join(headers) + " |"]
                md_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
                for r in rows:
                    md_lines.append("| " + " | ".join(r) + " |")
                raw_markdown = "\n".join(md_lines)

                tables.append(
                    PaperTable(
                        table_id=f"table_{tab_num}",
                        caption=caption,
                        page_number=page_number,
                        headers=headers,
                        rows=rows,
                        raw_markdown=raw_markdown,
                    )
                )

        return tables

    @staticmethod
    def find_numerical_candidates(table: PaperTable) -> List[Dict[str, str | float]]:
        """Scans table cells for numerical metric values (e.g. 91.4, 0.882, 28.4)."""
        candidates: List[Dict[str, str | float]] = []
        num_pattern = re.compile(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*(?:%|±\s*[0-9]+(?:\.[0-9]+)?)?\s*$")

        if not table.headers or not table.rows:
            return candidates

        for row_idx, row in enumerate(table.rows):
            row_label = row[0] if row else f"Row {row_idx + 1}"
            for col_idx, cell in enumerate(row):
                if col_idx == 0 and len(row) > 1:
                    continue

                match = num_pattern.match(cell)
                if match:
                    try:
                        val = float(match.group(1))
                        header_name = table.headers[col_idx] if col_idx < len(table.headers) else f"Col {col_idx}"
                        candidates.append({
                            "table_id": table.table_id,
                            "page_number": table.page_number,
                            "row": row_label,
                            "column": header_name,
                            "value": val,
                            "raw_cell": cell,
                        })
                    except ValueError:
                        continue

        return candidates
