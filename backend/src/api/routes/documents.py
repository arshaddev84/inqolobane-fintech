"""Read-only endpoints for synthetic source documents."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from schemas.source import SourceDocument, SourceDocumentListResponse
from services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])
document_service = DocumentService()


@router.get("", response_model=SourceDocumentListResponse)
def list_documents(
    search: Annotated[str | None, Query(max_length=120)] = None,
) -> SourceDocumentListResponse:
    """Search local Markdown source documents by text or linked reference."""
    return document_service.list_documents(search)


@router.get("/{document_ref}", response_model=SourceDocument)
def get_document(document_ref: str) -> SourceDocument:
    """Return a known repository document by its fixture basename."""
    document = document_service.get_document(document_ref)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document