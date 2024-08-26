from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker, relationship
from dotenv import load_dotenv
import os, datetime


load_dotenv()

engine = create_engine(url = os.getenv("DATABASE_URL"))
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Users(Base):
    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)
    chat_id = Column(Integer, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    profiles = relationship("Profiles", back_populates="user")


class Profiles(Base):
    __tablename__ = 'Profiles'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    user_id = Column(BigInteger, ForeignKey('Users.id'), nullable=False)
    mode = Column(Integer, nullable=False, default=0)
    text_format_id = Column(Integer, ForeignKey('Text_Formats.id'), nullable=False, default=1)
    is_completed = Column(Boolean, nullable=False, default=False)

    user = relationship("Users", back_populates="profiles")
    text_format = relationship("Text_Formats")
    topics_profiles = relationship("Topics_Profiles", back_populates="profile")


class Topics(Base):
    __tablename__ = 'Topics'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    name = Column(String(255), nullable=False, unique=True)
    url = Column(String(255), nullable=False, unique=True)

    topics_profiles = relationship("Topics_Profiles", back_populates="topic")
    news = relationship("News", back_populates="topic")


class Topics_Profiles(Base):
    __tablename__ = 'Topics_Profiles'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    profile_id = Column(BigInteger, ForeignKey('Profiles.id'), nullable=False)
    topic_id = Column(BigInteger, ForeignKey('Topics.id'), nullable=False)

    profile = relationship("Profiles", back_populates="topics_profiles")
    topic = relationship("Topics", back_populates="topics_profiles")


class Text_Formats(Base):
    __tablename__ = 'Text_Formats'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    name = Column(String(255), nullable=False, unique=True)

    profiles = relationship("Profiles", back_populates="text_format")


class News(Base):
    __tablename__ = 'News'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    link = Column(String(255), nullable=False, unique=True)
    topic_id = Column(BigInteger, ForeignKey('Topics.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    topic = relationship("Topics", back_populates="news")