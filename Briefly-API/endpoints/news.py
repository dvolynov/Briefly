from fastapi import APIRouter
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
from sqlalchemy import and_
from dotenv import load_dotenv
import configparser, os

from .deps import db_dependency, get_profile
from database import models
from modules import Scraper, GeminiChat
from .summary import create_model


load_dotenv()
config = configparser.ConfigParser()
config.read('config.ini')


router = APIRouter(tags=["News"])

scraper = Scraper()


@router.get("/{chat_id}")
def get_news(chat_id: str, hours: int, db: db_dependency):
    try:
        profile = get_profile(chat_id, db)
        topics = (
            db.query(models.Topics)
            .join(models.Topics_Profiles)
            .filter(models.Topics_Profiles.profile_id == profile.id)
            .all()
        )
        scraped_news = scraper(topics={i.name: i.url for i in topics})

        for item in scraped_news:

            topic = db.query(models.Topics).filter_by(name=item["topic"]).first()
            existing_news = db.query(models.News).filter_by(link=item["link"]).first()

            if not existing_news:
                new_news = models.News(
                    link = item["link"],
                    topic_id = topic.id
                )
                db.add(new_news)
                db.commit()

        three_hours_ago = datetime.utcnow() - timedelta(hours=hours)

        recent_news = (
            db.query(models.News)
            .join(models.Topics, models.News.topic_id == models.Topics.id)
            .join(models.Topics_Profiles, models.Topics.id == models.Topics_Profiles.topic_id)
            .filter(
                and_(
                    models.News.created_at >= three_hours_ago,
                    models.Topics_Profiles.profile_id == profile.id
                )
            )
            .all()
        )

        if not recent_news:
            raise HTTPException(status_code=402, detail="No recent news found for the user's preferences.")

        text_format = db.query(models.Text_Formats).filter_by(id=profile.text_format_id).first()

        instruction = open("text/news.txt").read().replace("<text_format>", text_format.name)
        instruction = instruction.replace("<text_format>", text_format.name)
        model = create_model(text_format, instruction)
        model.start()

        result = []

        for topic in topics:
            links = [
                news.link
                for news in recent_news
                if news.topic.name == topic.name
            ]
            print(len(links))
            links = "\n".join(links)
            if links:
                response = model(links)
                if response['status'] == "success":
                    result.append({
                        "topic": f"{response['data']['emoji']} {topic.name}",
                        "summary": response['data']['text']
                    })

        return {"news": result}


    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
