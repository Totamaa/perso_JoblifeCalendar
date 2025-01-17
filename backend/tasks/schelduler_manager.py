from apscheduler.schedulers.background import BackgroundScheduler

from services import PandascoreService

scheduler = BackgroundScheduler()

def start_scheduler():
    pandascore_service = PandascoreService()
    scheduler.add_job(pandascore_service.ask_pandascore(), "cron", hour=4, minute=30)
    scheduler.start()

def stop_scheduler():
    scheduler.shutdown()