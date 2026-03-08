"""
Utility helpers – thin wrappers around pageindex.utils that the services use.

Kept for potential custom extensions; most logic lives in the services layer.
"""

from typing import Any, Dict, List
import json


def load_notebook_data(notebook_path: str) -> Dict[str, Any]:
    """Load a Jupyter notebook JSON file."""
    with open(notebook_path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_code_cells(notebook_data: Dict[str, Any]) -> List[str]:
    """Return a list of concatenated source strings for each code cell."""
    return [
        "".join(cell["source"])
        for cell in notebook_data.get("cells", [])
        if cell.get("cell_type") == "code"
    ]


def truncate(text: str, max_chars: int = 1000) -> str:
    """Truncate text with an ellipsis when it exceeds *max_chars*."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."
