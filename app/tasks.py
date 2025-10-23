# app/tasks.py
from celery import Celery
import os

celery = Celery("tasks", broker=os.getenv("REDIS_URL", "redis://redis:6379/0"))


@celery.task(bind=True, max_retries=3)
def send_notification(self, patient_id, message, data=None):
    # stub: call FCM or push gateway
    print("send_notification", patient_id, message)
    return True
