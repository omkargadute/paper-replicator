"""Specialized scientific table extractor and numerical claim locator."""

import re
from typing import Dict, List, Optional, Tuple
from paperrep.schemas.paper import PaperTable


class TableExtractor:
    """Parses scientific benchmark tables to locate candidate numeric claims."""

    @staticmethod
    def find_numerical_candidates(table: PaperTable) -> List[Dict[str, str | float]]:
        """Scans table cells for numerical metric values (e.g. 91.4, 0.882, 28.4).
        
        Returns:
            List of candidate dictionaries with row, column, and extracted float value.
        """
        candidates: List[Dict[str, str | float]] = []
        num_pattern = re.compile(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*(?:%|±\s*[0-9]+(?:\.[0-9]+)?)?\s*$")

        if not table.headers or not table.rows:
            return candidates

        for row_idx, row in enumerate(table.rows):
            row_label = row[0] if row else f"Row {row_idx + 1}"
            for col_idx, cell in enumerate(row):
                if col_idx == 0 and len(row) > 1:
                    continue  # First column is usually model/dataset name

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
