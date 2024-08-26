from fastapi import APIRouter
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from .deps import db_dependency, get_profile
from database import models


router = APIRouter(tags=["Topics"])


@router.patch("/")
def update_topics(chat_id: int, topics: list[str], db: db_dependency):
    try:
        profile = get_profile(chat_id, db)

        existing_topics_profiles = db.query(models.Topics_Profiles).filter_by(profile_id=profile.id).all()
        existing_topic_ids = {tp.topic_id for tp in existing_topics_profiles}

        topic_ids_to_add = []
        for name in topics:
            topic = db.query(models.Topics).filter_by(name=name).first()
            if topic:
                topic_ids_to_add.append(topic.id)

        for tp in existing_topics_profiles:
            if tp.topic_id not in topic_ids_to_add:
                db.delete(tp)

        for topic_id in topic_ids_to_add:
            if topic_id not in existing_topic_ids:
                new_relation = models.Topics_Profiles(profile_id=profile.id, topic_id=topic_id)
                db.add(new_relation)

        db.commit()
        return {"message": "Topics updated successfully."}

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/{chat_id}")
def get_topics(chat_id: int, db: db_dependency):
    try:
        profile = get_profile(chat_id, db)
        topics = (
            db.query(models.Topics)
            .join(models.Topics_Profiles)
            .filter(models.Topics_Profiles.profile_id == profile.id)
            .all()
        )

        if not topics:
            return {"topics": []}

        return {"topics": [topic.name for topic in topics]}

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
def get_all_topics(db: db_dependency):
    try:
        topics = db.query(models.Topics).all()

        if not topics:
            return {"topics": []}

        return {"topics": [topic.name for topic in topics]}

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


