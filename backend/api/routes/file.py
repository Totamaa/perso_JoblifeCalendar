import os

from fastapi import APIRouter, HTTPException, status
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
    logging.info(f"Requesting calendar file receive with filters: lol={lol}, valo={valo}")
    try:
        file_path = "static/calendar.ics"
        return FileResponse(
            path=file_path,
            media_type="text/calendar",
            filename="calendar.ics"
        )
    except Exception as e:
        logging.error(f"Error filtering calendar: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error filtering calendar")