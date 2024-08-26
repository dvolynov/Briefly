from fastapi import APIRouter
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from .deps import db_dependency, get_profile
from database import models


router = APIRouter(tags=["Mode"])


@router.get("/{chat_id}")
def get_mode(chat_id: int, db: db_dependency):
    try:
        profile = get_profile(chat_id, db)
        print(profile)
        return {"mode": profile.mode}

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/")
def update_mode(mode: int, chat_id: int, db: db_dependency):
    try:
        profile = get_profile(chat_id, db)

        if mode in [0, 1]:
            if mode != profile.mode:
                profile.mode = mode
            else:
                return {"message": "Mode is the same"}
        else:
            raise HTTPException(status_code=404, detail="Mode must be 0 (text) or 1 (audio)")

        db.commit()
        return {"message": "Mode updated successfully."}

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
