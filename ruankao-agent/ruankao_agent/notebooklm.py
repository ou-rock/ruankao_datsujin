from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True, slots=True)
class NotebookLMSource:
    title: str
    url: str
    notebook_id: str
    local_library_id: str
    role: str = "selected external researcher for System Architecture Designer exam sources"

    def query_command(self, question: str) -> list[str]:
        return [
            "nlm",
            "query",
            "notebook",
            self.notebook_id,
            question,
            "--json",
        ]


DEFAULT_NOTEBOOK_SOURCE = NotebookLMSource(
    title="System Architecture Designer Exam Questions and Analysis",
    url="https://notebooklm.google.com/notebook/5d1ffc0c-2fef-47e2-ac3c-3b29a0ab8c0a",
    notebook_id="5d1ffc0c-2fef-47e2-ac3c-3b29a0ab8c0a",
    local_library_id="system-architecture-designer-e",
)


def notebooklm_source_summary(source: NotebookLMSource = DEFAULT_NOTEBOOK_SOURCE) -> str:
    return f"{source.title} [{source.local_library_id}]"


def notebooklm_query_command(question: str, source: NotebookLMSource = DEFAULT_NOTEBOOK_SOURCE) -> Sequence[str]:
    return source.query_command(question)
