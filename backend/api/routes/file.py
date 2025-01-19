import os
from datetime import datetime, timedelta
import hashlib
import time

from fastapi import APIRouter, HTTPException, Response, status, Request
from fastapi.responses import FileResponse

from config.logs import LoggerManager

router = APIRouter()
logging = LoggerManager()

@router.get(
    "/calendar.ics",
    response_class=FileResponse,
    status_code=200
)
async def get_calendar(request: Request, lol: bool = True, valo: bool = True):
    logging.info(f"Requesting calendar file receive with filters: lol={lol}, valo={valo}")
    try:
        file_path = "static/calendar.ics"
        
        file_stat = os.stat(file_path)
        last_modified = datetime.fromtimestamp(file_stat.st_mtime)
        last_modified_str = last_modified.strftime("%a, %d %b %Y %H:%M:%S GMT")
        
        etag = hashlib.md5(f"{file_stat.st_mtime}:{file_stat.st_size}".encode()).hexdigest()
        
        if_none_match = request.headers.get("if-none-match")
        if_modified_since = request.headers.get("if-modified-since")
        
        if (if_none_match and if_none_match == etag) or \
           (if_modified_since and datetime.strptime(if_modified_since, "%a, %d %b %Y %H:%M:%S GMT") >= last_modified):
            return Response(status_code=status.HTTP_304_NOT_MODIFIED)
        
        response = FileResponse(
            path=file_path,
            media_type="text/calendar",
            filename="calendar.ics"
        )
        
        cache_duration = timedelta(minutes=5)
        response.headers["Cache-Control"] = f"public, max-age={int(cache_duration.total_seconds())}"
        response.headers["Expires"] = (datetime.now() + cache_duration).strftime("%a, %d %b %Y %H:%M:%S GMT")
        
        response.headers["ETag"] = etag
        response.headers["Last-Modified"] = last_modified_str
        
        return response
        
    except Exception as e:
        logging.error(f"Error filtering calendar: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error filtering calendar")