from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Artifact, Space
from ..schemas import ArtifactCreate, ArtifactRead, ArtifactUpdate
from ..storage import remove_upload, save_upload

router = APIRouter(prefix="/artifacts", tags=["artifacts"])


@router.get("/", response_model=List[ArtifactRead])
def list_artifacts(
    space_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
) -> List[Artifact]:
    query = db.query(Artifact)
    if space_id is not None:
        query = query.filter(Artifact.space_id == space_id)
    return query.order_by(Artifact.created_at.desc()).all()


@router.post("/", response_model=ArtifactRead, status_code=status.HTTP_201_CREATED)
def create_artifact(artifact_in: ArtifactCreate, db: Session = Depends(get_db)) -> Artifact:
    space_exists = db.query(Space.id).filter(Space.id == artifact_in.space_id).first()
    if space_exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Space not found")

    payload = artifact_in.model_dump(exclude={"file_path"})
    artifact = Artifact(**payload)
    db.add(artifact)
    db.commit()
    db.refresh(artifact)
    return artifact


@router.get("/search", response_model=List[ArtifactRead])
def search_artifacts(
    q: str = Query(..., min_length=1),
    space_id: Optional[int] = Query(default=None),
    limit: int = Query(default=20, le=100),
    db: Session = Depends(get_db),
) -> List[Artifact]:
    query = db.query(Artifact)
    if space_id is not None:
        query = query.filter(Artifact.space_id == space_id)

    pattern = f"%{q}%"
    query = query.filter(
        or_(
            Artifact.title.ilike(pattern),
            Artifact.content.ilike(pattern),
            Artifact.file_name.ilike(pattern),
        )
    )
    return query.order_by(Artifact.created_at.desc()).limit(limit).all()


@router.post("/upload", response_model=ArtifactRead, status_code=status.HTTP_201_CREATED)
async def upload_artifact(
    space_id: int = Form(...),
    file: UploadFile = File(...),
    title: Optional[str] = Form(default=None),
    content: Optional[str] = Form(default=None),
    db: Session = Depends(get_db),
) -> Artifact:
    space_exists = db.query(Space.id).filter(Space.id == space_id).first()
    if space_exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Space not found")

    stored_name, original_name, mime_type = await save_upload(file)

    artifact = Artifact(
        space_id=space_id,
        title=title or original_name,
        content=content,
        file_name=original_name,
        file_path=stored_name,
        mime_type=mime_type,
    )
    db.add(artifact)
    db.commit()
    db.refresh(artifact)
    return artifact


@router.get("/{artifact_id}", response_model=ArtifactRead)
def get_artifact(artifact_id: int, db: Session = Depends(get_db)) -> Artifact:
    artifact = db.query(Artifact).filter(Artifact.id == artifact_id).first()
    if artifact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Artifact not found"
        )
    return artifact


@router.put("/{artifact_id}", response_model=ArtifactRead)
def update_artifact(
    artifact_id: int, artifact_in: ArtifactUpdate, db: Session = Depends(get_db)
) -> Artifact:
    artifact = db.query(Artifact).filter(Artifact.id == artifact_id).first()
    if artifact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Artifact not found"
        )

    for field, value in artifact_in.model_dump(exclude_unset=True, exclude={"file_path"}).items():
        setattr(artifact, field, value)

    db.commit()
    db.refresh(artifact)
    return artifact


@router.delete("/{artifact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_artifact(artifact_id: int, db: Session = Depends(get_db)) -> None:
    artifact = db.query(Artifact).filter(Artifact.id == artifact_id).first()
    if artifact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Artifact not found"
        )

    remove_upload(artifact.file_path)
    db.delete(artifact)
    db.commit()
