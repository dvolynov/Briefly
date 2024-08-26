from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from typing import Annotated
from dotenv import load_dotenv
import configparser, os

from database import SessionLocal, models
from modules import GeminiChat


load_dotenv()

config = configparser.ConfigParser()
config.read('config.ini')


MODELS = {}

create_model = lambda text_format, instruction: GeminiChat(
    api_key            = os.getenv('GEMINI_API_KEY'),
    system_instruction = instruction,
    model_name         = config.get('Model', 'model_name'),
    max_output_tokens  = config.getint('Model', 'max_output_tokens'),
    temperature        = config.getfloat('Model', 'temperature'),
    input_words_limit  = config.getfloat('Model', 'input_words_limit')
)


def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()


db_dependency = Annotated[Session, Depends(get_db)]


def get_profile(chat_id, db):
    user = db.query(models.Users).filter_by(chat_id=chat_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found with the given chat_id.")

    profile = db.query(models.Profiles).filter_by(user_id=user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found for the given user.")

    return profile