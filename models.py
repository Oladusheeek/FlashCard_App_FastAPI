from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# USERS=============================

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
# ==================================

# Sections==========================

class SectionBase(BaseModel):
    title: str

class SectionCreate(SectionBase):
    pass

class SectionResponse(SectionBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class SectionUpdate(BaseModel):
    title: Optional[str] = None

# ==================================

# Card Sets ========================
class CardSetBase(BaseModel):
    title: str
    description: Optional[str] = None

class CardSetCreate(CardSetBase):
    pass

class CardSetResponse(CardSetBase):
    id: int
    section_id: int

    class Config:
        from_attributes = True

class CardSetUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

# ==================================

# Cards =============================

class CardBase(BaseModel):
    front_side: str
    back_side: str

class CardCreate(CardBase):
    pass

class CardResponse(CardBase):
    id: int
    card_set_id: int
    is_learned: bool
    created_at: datetime
    next_review_at: Optional[datetime] = None
    interval: Optional[float] = None
    easiness_factor: Optional[float] = None
    repetitions: Optional[int] = None

    class Config:
        from_attributes = True

class CardUpdate(BaseModel):
    front_side: Optional[str] = None
    back_side: Optional[str] = None
    is_learned: Optional[bool] = None

class CardStatusUpdate(BaseModel):
    is_learned: bool

class CardReview(BaseModel):
    quality: int
# ====================================
