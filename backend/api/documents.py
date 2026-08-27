from pathlib import Path
from tempfile import NamedTemporaryFile
import sys

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)

from sqlalchemy.orm import Session

from database.database import get_db
from database.models import Document, User
from auth.dependencies import get_current_user


PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from config import load_settings
from ingest import ingest_file
from embeddings import GeminiEmbedder
from qdrant_store import QdrantStore


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".md",
    ".txt",
}


settings = load_settings()

store = QdrantStore(settings)

embedder = GeminiEmbedder(settings)

store.ensure_collection()


@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required",
        )

    original_filename = Path(
        file.filename
    ).name

    extension = Path(
        original_filename
    ).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, MD, and TXT files are supported",
        )

    # Prevent the same filename from being uploaded
    # multiple times for the same user.
    existing_document = (
        db.query(Document)
        .filter(
            Document.user_id == current_user.id,
            Document.filename == original_filename,
        )
        .first()
    )

    if existing_document is not None:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Document '{original_filename}' already exists "
                "in your knowledge base. Delete the existing "
                "document first if you want to upload it again."
            ),
        )

    temp_path = None

    try:

        with NamedTemporaryFile(
            suffix=extension,
            delete=False,
        ) as temp_file:

            content = file.file.read()

            temp_file.write(content)

            temp_path = Path(
                temp_file.name
            )

        result = ingest_file(
            path=temp_path,
            store=store,
            embedder=embedder,
            settings=settings,
            user_id=current_user.id,
            original_filename=original_filename,
        )

        document = Document(
            user_id=current_user.id,
            knowledge_base_doc_id=result["doc_id"],
            filename=original_filename,
            file_type=extension[1:],
        )

        db.add(document)

        db.commit()

        db.refresh(document)

        return {
            "message": "Document uploaded successfully",
            "document": {
                "id": document.id,
                "knowledge_base_doc_id": (
                    document.knowledge_base_doc_id
                ),
                "filename": document.filename,
                "file_type": document.file_type,
                "created_at": document.created_at,
            },
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Document upload failed: {str(e)}",
        )

    finally:

        if (
            temp_path is not None
            and temp_path.exists()
        ):
            try:
                temp_path.unlink()
            except Exception:
                pass


@router.get("/")
def list_user_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    documents = (
        db.query(Document)
        .filter(
            Document.user_id == current_user.id
        )
        .order_by(
            Document.created_at.desc()
        )
        .all()
    )

    return {
        "documents": [
            {
                "id": document.id,
                "knowledge_base_doc_id": (
                    document.knowledge_base_doc_id
                ),
                "filename": document.filename,
                "file_type": document.file_type,
                "created_at": document.created_at,
            }
            for document in documents
        ]
    }


@router.get("/{document_id}")
def get_user_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.user_id == current_user.id,
        )
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return {
        "id": document.id,
        "knowledge_base_doc_id": (
            document.knowledge_base_doc_id
        ),
        "filename": document.filename,
        "file_type": document.file_type,
        "created_at": document.created_at,
    }


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.user_id == current_user.id,
        )
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    if document.knowledge_base_doc_id:

        try:

            store.delete_document(
                document.knowledge_base_doc_id,
                current_user.id,
            )

        except Exception:
            pass

    db.delete(document)

    db.commit()

    return {
        "message": "Document deleted successfully"
    }