from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Section(Base):
    __tablename__ = "sections"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)

class Card_set(Base):
    __tablename__ = "card_sets"
    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("sections.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)

class Card(Base):
    __tablename__ = "cards"
    id = Column(Integer, primary_key=True, index=True)
    card_set_id = Column(Integer, ForeignKey("card_sets.id", ondelete="CASCADE"), nullable=False)
    front_side = Column(String, nullable=False)
    back_side = Column(String, nullable=False)
    is_learned = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default = func.now())
    next_review_at = Column(DateTime(timezone=True), server_default= func.now() ) 
    interval = Column(Float, default=0.0)
    easiness_factor = Column(Float, default= 2.5)
    repetitions = Column(Integer, default=0)