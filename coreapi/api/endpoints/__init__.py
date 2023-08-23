from fastapi import APIRouter

from .user import router as user_router
from .aiagent import router as ai_agent_router
from .sampledialog import router as sample_dialog_router
from .samplevoice import router as sample_voice_router
from .file import router as file_router
from .login import router as login_router
from .webhook import router as webhook_router

router = APIRouter()

router.include_router(user_router)
router.include_router(ai_agent_router)
router.include_router(sample_dialog_router)
router.include_router(sample_voice_router)
router.include_router(file_router)
router.include_router(login_router)
router.include_router(webhook_router)