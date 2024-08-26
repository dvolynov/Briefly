from fastapi import APIRouter, UploadFile
from fastapi import HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import configparser, os, io
from youtube_transcript_api import YouTubeTranscriptApi
from pypdf import PdfReader

from .deps import db_dependency, get_profile, MODELS, create_model
from modules import SpeechKit


load_dotenv()

config = configparser.ConfigParser()
config.read('config.ini')

kit = SpeechKit(
    deegram_api_key    = os.getenv('DEEPGRAM_API_KEY'),
    elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY'),
    voice              = config.get('Elevenlabs', 'voice'),
    model              = config.get('Elevenlabs', 'model')
)

router = APIRouter(tags=["Summary"])


def get_model(chat_id, text_format):
    model = MODELS.get(chat_id)

    if (not model) or (model['format'] != text_format):
        instruction = open("text/instruction.txt").read()
        instruction = instruction.replace("<text_format>", text_format)
        model = create_model(text_format, instruction)
        model.start()
        MODELS[chat_id] = {
            "model": model,
            "format": text_format
        }
    else:
        model = model['model']
    return model



class Message(BaseModel): message: str
class Text(BaseModel): text: str
class Url(BaseModel): url: str



@router.patch("/clear_cache")
async def clear_cache(chat_id: int, db: db_dependency):
    model = MODELS.get(chat_id)
    if model:
        del MODELS[chat_id]
    return {"message": "Cache is cleared"}



@router.post("/pdf")
async def get_pdf_summary(chat_id: int, file: UploadFile, db: db_dependency):
    try:
        binary = await file.read()
        reader = PdfReader(io.BytesIO(binary))

        text = ""
        for page in reader.pages:
            text += page.extract_text()

        text = text.replace("\n", " ")

        if not text:
            raise HTTPException(status_code=404, detail="No text detected")
    except:
        raise HTTPException(status_code=404, detail="Unable to read a PDF-file")

    text = f"PDF file:\n\n{text}"
    return summarize(chat_id, text, db)



@router.post("/video")
async def get_video_summary(chat_id: int, video_id: str, db: db_dependency):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(
            video_id=video_id,
            languages=['en']
        )
        text = " ".join([i['text'] for i in transcript]).replace("\n", " ")
        if not text:
            raise HTTPException(status_code=404, detail="No text detected")
    except:
        raise HTTPException(status_code=404, detail="Unable to read video")

    text = f"YouTube video:\n\n{text}"
    return summarize(chat_id, text, db)



@router.post("/file")
async def get_file_summary(chat_id: int, file: UploadFile, db: db_dependency):
    try:
        binary = await file.read()
        text = str(binary.decode('utf-8'))
    except:
        raise HTTPException(status_code=404, detail="Unable to read file")

    if not text:
        raise HTTPException(status_code=404, detail="No text detected")
    text = f"Text file:\n\n{text}"
    return summarize(chat_id, text, db)



@router.post("/url")
def get_url_summary(chat_id: int, url: Url, db: db_dependency):
    if not url:
        raise HTTPException(status_code=404, detail="No url detected")
    message_text = f"Url:\n\n{url.url}"
    return summarize(chat_id, message_text, db)



@router.post("/text")
def get_text_summary(chat_id: int, text: Text, db: db_dependency):
    if not text:
        raise HTTPException(status_code=404, detail="No text detected")
    message_text = f"Text:\n\n{text.text}"
    return summarize(chat_id, message_text, db)



@router.post("/audio")
async def get_audio_summary(chat_id: int, file: UploadFile, db: db_dependency):
    binary = await file.read()
    message_text = kit.speech_to_text(binary)
    if not message_text:
        raise HTTPException(status_code=404, detail="No words detected")

    message_text = f"Audio file:\n\n{message_text}"
    return summarize(chat_id, message_text, db)



@router.post("/model_voice_control")
async def model_voice_control(chat_id: int, file: UploadFile, db: db_dependency):
    try:
        if not MODELS.get(chat_id):
            raise HTTPException(status_code=404, detail="Cache is clear. Nothing to control")
        binary = await file.read()
        message_text = kit.speech_to_text(binary)
        if not message_text:
            raise HTTPException(status_code=404, detail="Empty voice message")
    except:
        raise HTTPException(status_code=404, detail="Unable read a voice message")
    return summarize(chat_id, message_text, db)



@router.post("/model_text_control")
async def model_text_control(chat_id: int, message: Message, db: db_dependency):
    if not MODELS.get(chat_id):
        raise HTTPException(status_code=404, detail="Cache is clear. Nothing to control")
    return summarize(chat_id, message.message, db)



def summarize(chat_id, text, db):
    try:
        profile = get_profile(chat_id, db)
        model = get_model(chat_id, profile.text_format.name)
        response = model(text)

        if response['status'] == "success":
            return {
                "title": f"{response['data']['emoji']} {response['data']['title']}",
                "summary": response['data']['text']
            }

        return response["details"]

    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))



@router.post("/compress/")
def compress(chat_id: int, text: Text, db: db_dependency):
    try:
        profile = get_profile(chat_id, db)
        instruction = open("text/compress.txt").read()
        model = create_model(profile.text_format.name, instruction)
        model.start()
        response = model(text.text)

        if response['status'] == "success":
            return {"text": response["data"]["text"].replace('"', "'")}

        raise HTTPException(status_code=404, detail=response['details'])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))