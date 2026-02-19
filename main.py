from fastapi import FastAPI

from database import engine
import database_models 

from routers import auth, sections, card_sets, cards
from fastapi.middleware.cors import CORSMiddleware

database_models.Base.metadata.create_all(bind=engine) 

app = FastAPI()
app.include_router(auth.router)
app.include_router(sections.router)
app.include_router(card_sets.router)
app.include_router(cards.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)