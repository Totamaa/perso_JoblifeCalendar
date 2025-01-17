
from config.logs import LoggerManager

class CalendarService:
    def __init__(self):
        self.logging = LoggerManager()
        
    def update_calendar_file(self):
        #TODO update calendar file from riot API
        pass
    
    def get_calendar_file(self):
        #TODO get calendar file with filter
        pass