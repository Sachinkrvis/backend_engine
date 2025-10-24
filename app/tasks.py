# app/tasks.py
from celery import Celery
import os

# from app.notifications import send_fcm_notification

celery = Celery("tasks", broker=os.getenv("REDIS_URL", "redis://redis:6379/0"))


# @celery.task(bind=True, max_retries=3)
# def send_notification(self, patient_id, message, data=None):
#     # Example: fetch token from DB here if needed
#     send_fcm_notification(token="DEVICE_TOKEN", title="Alert", body=message, data=data or {})
#     return True


@celery.task(bind=True, max_retries=3)
def send_notification(self, patient_id, message, data=None):
    # stub: call FCM or push gateway
    print("send_notification", patient_id, message)
    return True
