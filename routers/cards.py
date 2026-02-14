from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import List
from datetime import datetime, timedelta, timezone

from database import SessionLocal, engine, get_db
import database_models 
from models import (

    CardCreate, CardResponse, CardUpdate, CardReview
)
from security import get_current_user_id

router = APIRouter(tags=["Cards"])

@router.post("/card_sets/{set_id}/cards", response_model=CardResponse)
def create_card(set_id: int, card: CardCreate, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    existing_card_set = db.query(database_models.Card_set).join(database_models.Section).filter(database_models.Card_set.id == set_id, database_models.Section.user_id == user_id).first()
    if not existing_card_set:
        raise HTTPException(status_code=403, detail="Access denied! Not your card_set!")
    
    new_card = database_models.Card(
        card_set_id=set_id,
        front_side = card.front_side,
        back_side = card.back_side
    )
    db.add(new_card)
    db.commit()
    db.refresh(new_card)
    return new_card

@router.get("/card_sets/{set_id}/cards", response_model=List[CardResponse])
def get_cards(set_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    cards = db.query(database_models.Card).join(database_models.Card_set).join(database_models.Section).filter(database_models.Card.card_set_id == set_id, database_models.Section.user_id == user_id).all()
    return cards

@router.get("/cards/mix", response_model=List[CardResponse])
def get_mix_cards(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db), limit: int = 10):

    now = datetime.now(timezone.utc)

    mixed_cards =   (
                        db.query(database_models.Card).join(database_models.Card_set).join(database_models.Section)
                        .filter(database_models.Section.user_id == user_id, database_models.Card.next_review_at <= now)
                        .order_by(func.random())
                        .limit(limit)
                        .all()
                    )
    return mixed_cards

@router.delete("/cards/{card_id}")
def delete_card(card_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    found_card = db.query(database_models.Card).join(database_models.Card_set).join(database_models.Section).filter(database_models.Card.id == card_id, database_models.Section.user_id == user_id).first()
    if not found_card:
        raise HTTPException(status_code=404, detail="Card not found!")
    db.delete(found_card)
    db.commit()

    return {"operation": "delete card", "success": True}   

@router.patch("/cards/{card_id}", response_model=CardResponse)
def card_update(card_id: int, card_data: CardUpdate, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    found_card = db.query(database_models.Card).join(database_models.Card_set).join(database_models.Section).filter(database_models.Card.id == card_id, database_models.Section.user_id == user_id ).first()
    if not found_card:
        raise HTTPException(status_code=404, detail="Card not found!")
    update_data = card_data.model_dump(exclude_unset=True)

    print(f"Data received from client: {card_data}")
    print(f"Dict for updating: {update_data}")

    for key, value in update_data.items():
        setattr(found_card, key, value)
    db.commit()
    db.refresh(found_card)
    return found_card

@router.post("/cards/{card_id}/review", response_model=CardResponse)
def review_card(card_id: int, review: CardReview, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    found_card = (db.query(database_models.Card)
                  .join(database_models.Card_set)
                  .join(database_models.Section)
                  .filter(database_models.Card.id == card_id, database_models.Section.user_id == user_id)
                  .first()
                )
    if not found_card:
        raise HTTPException(status_code=404, detail="Card not found")
    
    q = review.quality

    if q < 2:
        found_card.repetitions = 0
        found_card.interval = 1
    else:
        new_easiness_factor = found_card.easiness_factor + (0.1 - (3 - q) * (0.08 + (3 - q) * 0.02))
        found_card.easiness_factor = max(1.3, new_easiness_factor)

        found_card.repetitions +=1
        if found_card.repetitions == 1:
            found_card.interval = 1
        elif found_card.repetitions == 2:
            found_card.interval = 6
        else:
            found_card.interval = found_card.interval * found_card.easiness_factor
    found_card.next_review_at = datetime.now(timezone.utc) + timedelta(days=found_card.interval)

    db.commit()
    db.refresh(found_card)

    return found_card

@router.get("/cards/due", response_model=List[CardResponse])
def get_due_cards(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)

    due_cards = (db.query(database_models.Card)
                 .join(database_models.Card_set)
                 .join(database_models.Section)
                 .filter(database_models.Card.next_review_at <= now, database_models.Section.user_id == user_id)
                 .order_by(database_models.Card.next_review_at.asc())
                 .all()
    )
    return due_cards