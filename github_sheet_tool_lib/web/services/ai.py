from __future__ import annotations

from typing import Any, Dict, List


class AIScoringService:
    """Simple local AI-like summarizer for grading comments."""

    def summarize_file_notes(self, files: List[Dict[str, Any]]) -> str:
        notes: List[str] = []
        for f in files[:3]:
            f_notes = f.get("notes", []) if isinstance(f, dict) else []
            if isinstance(f_notes, list):
                notes.extend([str(n) for n in f_notes[:2]])
        if not notes:
            return "Chua du du lieu de nhan xet."
        return " | ".join(notes[:5])

    def risk_label(self, score_10: float, high_risk_plagiarism: bool) -> str:
        if high_risk_plagiarism:
            return "CANH_BAO_DAO_CODE"
        if score_10 < 5.0:
            return "DIEM_THAP"
        if score_10 < 7.0:
            return "CAN_CAI_THIEN"
        return "TOT"
