from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from ..db import get_db
from ..models import Space
from ..schemas import SpaceCreate, SpaceDetail, SpaceRead, SpaceUpdate

router = APIRouter(prefix="/spaces", tags=["spaces"])


@router.get("/", response_model=List[SpaceRead])
def list_spaces(db: Session = Depends(get_db)) -> List[Space]:
    return db.query(Space).order_by(Space.created_at.desc()).all()


@router.post("/", response_model=SpaceRead, status_code=status.HTTP_201_CREATED)
def create_space(space_in: SpaceCreate, db: Session = Depends(get_db)) -> Space:
    space = Space(**space_in.model_dump())
    db.add(space)
    db.commit()
    db.refresh(space)
    return space


@router.get("/{space_id}", response_model=SpaceDetail)
def get_space(space_id: int, db: Session = Depends(get_db)) -> Space:
    space = (
        db.query(Space)
        .options(selectinload(Space.artifacts))
        .filter(Space.id == space_id)
        .first()
    )
    if space is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Space not found")
    return space


@router.put("/{space_id}", response_model=SpaceRead)
def update_space(
    space_id: int, space_in: SpaceUpdate, db: Session = Depends(get_db)
) -> Space:
    space = db.query(Space).filter(Space.id == space_id).first()
    if space is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Space not found")

    for field, value in space_in.model_dump(exclude_unset=True).items():
        setattr(space, field, value)

    db.commit()
    db.refresh(space)
    return space


@router.delete("/{space_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_space(space_id: int, db: Session = Depends(get_db)) -> None:
    space = db.query(Space).filter(Space.id == space_id).first()
    if space is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Space not found")

    db.delete(space)
    db.commit()
