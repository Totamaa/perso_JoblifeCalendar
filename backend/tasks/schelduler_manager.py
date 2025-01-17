from apscheduler.schedulers.background import BackgroundScheduler

from services import EsportCalendarService

scheduler = BackgroundScheduler()

def start_scheduler():
    esport_calendar_service = EsportCalendarService()
    scheduler.add_job(esport_calendar_service.update_calendar, "interval", minutes=1)
    scheduler.start()

def stop_scheduler():
    scheduler.shutdown()