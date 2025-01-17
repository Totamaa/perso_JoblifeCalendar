import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from config.logs import LoggerManager

router = APIRouter()
logging = LoggerManager()

@router.get(
    "/calendar.ics",
    response_class=FileResponse,
    status_code=200
)
async def get_calendar(lol: bool = True, valo: bool = True):
    try:
        file_path = "static/calendar.ics"
        return FileResponse(
            path=file_path,
            media_type="text/calendar",
            filename="calendar.ics"
        )
    except Exception:
        raise HTTPException(status_code=500)