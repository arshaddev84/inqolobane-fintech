"""Checks for the local synthetic document catalog."""

from pathlib import Path

from services.document_service import DocumentService


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def test_document_catalog_loads_local_sources_and_extracts_references() -> None:
    """The catalog returns known Markdown sources with searchable case references."""
    service = DocumentService(REPOSITORY_ROOT / "data" / "documents")

    results = service.list_documents()
    matching = service.list_documents("CMP-2001")

    assert results.total == 50
    assert len(results.items) == 50
    assert matching.total == 2
    assert all("CMP-2001" in document.related_refs for document in matching.items)


def test_document_lookup_rejects_unknown_path_like_references() -> None:
    """Document lookup only accepts exact Markdown fixture basenames."""
    service = DocumentService(REPOSITORY_ROOT / "data" / "documents")

    assert service.get_document("../sql/schema") is None