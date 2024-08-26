from fastapi import APIRouter
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from .deps import db_dependency, get_profile
from database import models


router = APIRouter(tags=["User"])


@router.put("/")
def add_user(db: db_dependency, chat_id: int, first_name: str = None, last_name: str = None, username: str = None):
    try:
        new_user = models.Users(
            first_name = first_name,
            last_name = last_name,
            username = username,
            chat_id = chat_id
        )
        db.add(new_user)
        db.commit()

        new_profile = models.Profiles(user_id = new_user.id)
        db.add(new_profile)
        db.commit()

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{chat_id}")
def user_exists(chat_id: int, db: db_dependency):
    try:
        user = db.query(models.Users).filter_by(chat_id=chat_id).first()
        if not user:
            return {"is_user": False}
        return {"is_user": True}

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/is_completed/{chat_id}")
def get_is_completed(chat_id: int, db: db_dependency):
    try:
        profile = get_profile(chat_id, db)
        return {"is_completed": profile.is_completed}

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/is_completed/{chat_id}")
def update_is_completed(chat_id: int, is_completed: bool, db: db_dependency):
    try:
        profile = get_profile(chat_id, db)
        profile.is_completed = is_completed
        db.commit()
        return {"message": "Profile updated successfully."}

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))