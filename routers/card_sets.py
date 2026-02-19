from fastapi import  APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import SessionLocal, engine, get_db
import database_models 
from models import (
    CardSetCreate, CardSetResponse, CardSetUpdate,
)
from security import get_current_user_id

router = APIRouter(tags=["Card Sets"])

@router.post("/sections/{section_id}/card_sets", response_model=CardSetResponse)
def create_card_set(section_id: int, card_set: CardSetCreate, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    existing_section = db.query(database_models.Section).filter(database_models.Section.id == section_id, database_models.Section.user_id == user_id).first()    
    if not existing_section:
        raise HTTPException(status_code=403, detail="Access denied! Not your section!")
    
    new_card_set = database_models.Card_set(
        section_id = section_id,
        title = card_set.title,
        description = card_set.description
    )

    db.add(new_card_set)
    db.commit()
    db.refresh(new_card_set)
    return new_card_set

@router.get("/sections/{section_id}/card_sets", response_model=List[CardSetResponse])
def get_card_sets(section_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    card_sets = db.query(database_models.Card_set).join(database_models.Section).filter(database_models.Card_set.section_id == section_id, database_models.Section.user_id == user_id).all()
    return card_sets

@router.delete("/card_sets/{set_id}")
def delete_card_set(set_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    found_card_set = db.query(database_models.Card_set).join(database_models.Section).filter(database_models.Card_set.id == set_id, database_models.Section.user_id == user_id).first()
    if not found_card_set:
        raise HTTPException(status_code=404, detail="Card set not found!")
    db.delete(found_card_set)
    db.commit()

    return {"operation": "delete card_set", "success": True} 

@router.patch("/card_sets/{set_id}", response_model=CardSetResponse)
def card_set_update(set_id: int, card_set_data: CardSetUpdate, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    found_set = db.query(database_models.Card_set).join(database_models.Section).filter(database_models.Card_set.id == set_id, database_models.Section.user_id == user_id).first()
    if not found_set:
        raise HTTPException(status_code=404, detail="Card set not found!")
    update_data = card_set_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(found_set, key, value)

    db.commit()
    db.refresh(found_set)
    return found_set