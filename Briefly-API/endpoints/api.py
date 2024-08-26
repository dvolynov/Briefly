from fastapi import APIRouter

from .mode import router as mode_router
from .news import router as news_router
from .summary import router as summary_router
from .text_format import router as text_format_router
from .topics import router as topics_router
from .user import router as user_router


router = APIRouter()

router.include_router(mode_router, prefix='/mode')
router.include_router(news_router, prefix='/news')
router.include_router(summary_router, prefix='/summary')
router.include_router(text_format_router, prefix='/text_format')
router.include_router(topics_router, prefix='/topics')
router.include_router(user_router, prefix='/user')



