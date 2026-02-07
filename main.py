from fastapi import FastAPI

from database import engine
import database_models 

from routers import auth, sections, card_sets, cards

database_models.Base.metadata.create_all(bind=engine) 

app = FastAPI()
app.include_router(auth.router)
app.include_router(sections.router)
app.include_router(card_sets.router)
app.include_router(cards.router)