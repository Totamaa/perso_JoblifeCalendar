import json
from fastapi import APIRouter

from config.logs import LoggerManager

router = APIRouter()
logging = LoggerManager()

@router.get(
    "/calendar.ics"
)
def get_calendar(leagueoflegend: bool = True, valorant: bool = True):
    logging.info(f"get_calendar recieve with params {"league of legends" if leagueoflegend else ""} {"valorant" if valorant else ""}")
    result = []
    if leagueoflegend:
        result.append("League of legend result")
        
    if valorant:
        result.append("Valorant result")
        
    return json.dumps(result)