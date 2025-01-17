import requests
from dotmap import DotMap

from config.logs import LoggerManager
from config.settings import get_settings

class PandascoreService:
    def __init__(self):
        self.logging = LoggerManager()
        settings = get_settings()
        self.base_url = settings.BACK_PANDA_BASE_URL
        self.id_jl_lol = settings.BACK_PANDA_ID_JL_LOL
        self.panda_api_key = settings.BACK_PANDA_API_KEY
        
    def ask_pandascore(self):
        url = f"{self.base_url}/"
        headers = {
            "Autorisation": f"Bearer {self.panda_api_key}",
            "Accept": "application/json"
        }
        
        response = requests.get(
            url,
            headers=headers
        )
        
        response.raise_for_status
        data = DotMap(response.json())
        print(data)
        
        
service = PandascoreService()
service.ask_pandascore()
