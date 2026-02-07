from fastapi import FastAPI, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List

from database import SessionLocal, engine, get_db
import database_models 
from models import (
    SectionCreate, SectionResponse, SectionUpdate
)
from security import get_current_user_id

router = APIRouter(tags=["Sections"])

@router.post("/sections", response_model=SectionResponse)
def create_section(section: SectionCreate, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    new_section = database_models.Section(
        user_id = user_id,
        title = section.title
    )

    db.add(new_section)
    db.commit()
    db.refresh(new_section)

    return new_section

@router.get("/sections", response_model=List[SectionResponse])
def get_sections(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    sections = db.query(database_models.Section).filter(database_models.Section.user_id == user_id).all()
    return sections

@router.delete("/sections/{section_id}")
def delete_section(section_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    found_section = db.query(database_models.Section).filter(database_models.Section.id == section_id, database_models.Section.user_id == user_id).first()
    if not found_section:
        raise HTTPException(status_code=404, detail="Section not found!")
    db.delete(found_section)
    db.commit()
    return {"operation": "delete section", "success": True}

@router.patch("/sections/{section_id}", response_model=SectionResponse)
def section_update(section_id: int, section_data: SectionUpdate, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    found_section = db.query(database_models.Section).filter(database_models.Section.id == section_id, database_models.Section.user_id == user_id).first()
    if not found_section:
        raise HTTPException(status_code=404, detail="Section not found!")
    found_section.title = section_data.title

    db.commit()
    db.refresh(found_section)
    return found_section