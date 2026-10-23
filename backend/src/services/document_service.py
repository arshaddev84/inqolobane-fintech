"""Catalog and search the repository's local synthetic Markdown documents."""

import re
from pathlib import Path

from schemas.source import SourceDocument, SourceDocumentListResponse

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
DOCUMENT_DIRECTORY = REPOSITORY_ROOT / "data" / "documents"
REFERENCE_PATTERN = re.compile(r"\b(?:CMP|CUS|ACC)-\d+\b|\bDOC-[A-Z]+-\d+\b")
DOCUMENT_REFERENCE_PATTERN = re.compile(
    r"^-\s+\*\*Document reference:\*\*\s*(.+?)\s*$",
    re.MULTILINE,
)


class DocumentService:
    """Read documents from the fixed repository fixture directory."""

    def __init__(self, document_directory: Path = DOCUMENT_DIRECTORY) -> None:
        self._document_directory = document_directory

    def list_documents(self, search: str | None = None) -> SourceDocumentListResponse:
        """Return all documents or those matching a text/reference query."""
        documents = [self._read_document(path) for path in sorted(self._document_directory.glob("*.md"))]
        documents_by_ref = {document.document_ref: document for document in documents}
        linked_case_refs: dict[str, set[str]] = {}
        for document in documents:
            case_refs = {ref for ref in document.related_refs if ref.startswith("CMP-")}
            for reference in document.related_refs:
                if reference in documents_by_ref and reference != document.document_ref:
                    linked_case_refs.setdefault(reference, set()).update(case_refs)
        documents = [
            document.model_copy(
                update={
                    "related_refs": sorted(
                        set(document.related_refs)
                        | linked_case_refs.get(document.document_ref, set())
                    )
                }
            )
            for document in documents
        ]
        if search:
            normalized_search = search.casefold()
            documents = [
                document
                for document in documents
                if normalized_search in document.title.casefold()
                or normalized_search in document.document_ref.casefold()
                or normalized_search in document.content.casefold()
                or any(normalized_search in reference.casefold() for reference in document.related_refs)
            ]
        return SourceDocumentListResponse(items=documents, total=len(documents))

    def get_document(self, document_ref: str) -> SourceDocument | None:
        """Find a document by its fixture basename without accepting arbitrary paths."""
        for path in self._document_directory.glob("*.md"):
            document = self._read_document(path)
            if path.stem == document_ref or document.document_ref == document_ref:
                return document
        return None

    @staticmethod
    def _read_document(path: Path) -> SourceDocument:
        content = path.read_text(encoding="utf-8")
        document_reference = DOCUMENT_REFERENCE_PATTERN.search(content)
        title = next(
            (line.removeprefix("# ").strip() for line in content.splitlines() if line.startswith("# ")),
            path.stem,
        )
        return SourceDocument(
            document_ref=document_reference.group(1) if document_reference else path.stem,
            filename=path.name,
            title=title,
            related_refs=sorted(set(REFERENCE_PATTERN.findall(content))),
            content=content,
        )