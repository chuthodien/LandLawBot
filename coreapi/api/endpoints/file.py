import os
from typing import Optional
from fastapi import APIRouter, Form
from fastapi.responses import FileResponse

router = APIRouter()

base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
assets_dir = "assets"
assets_path = os.path.join(base_path, assets_dir)

@router.get("/assets/{file_fodel}/{aiagent_id}/{file_name}")
async def read_file(
    file_fodel: str,
    aiagent_id: int,
    file_name: str
):
    file_path = os.path.join(assets_path, file_fodel, str(aiagent_id), file_name)
    if not os.path.exists(file_path):
        return {"error": f"File '{file_name}' not found."}
    return FileResponse(file_path)