from fastapi import APIRouter
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from .deps import db_dependency, get_profile
from database import models


router = APIRouter(tags=["Text Format"])


@router.patch("/")
def update_text_format(chat_id: int, format: str, db: db_dependency):
    try:
        profile = get_profile(chat_id, db)
        format = db.query(models.Text_Formats).filter_by(name=format).first()
        if not format:
            raise HTTPException(status_code=404, detail="Text format not found.")

        profile.text_format_id = format.id

        db.commit()
        return {"message": "Text format updated successfully."}

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{chat_id}")
def get_text_format(chat_id: int, db: db_dependency):
    try:
        profile = get_profile(chat_id, db)
        text_format = db.query(models.Text_Formats).filter_by(id=profile.text_format_id).first()
        if not text_format:
            raise HTTPException(status_code=404, detail="Text format not found.")

        return {"text_format": text_format.name}

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
def get_all_text_formats(db: db_dependency):
    try:
        text_formats = db.query(models.Text_Formats).all()

        if not text_formats:
            return {"text_formats": []}

        return {"text_formats": [text_format.name for text_format in text_formats]}

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
