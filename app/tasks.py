# app/tasks.py
import os
from celery import Celery
from app.database import AsyncSessionLocal
from app.models import RecommendationState, RecommendationAudit, DeviceToken
from app.notifications import send_fcm_notification
from sqlalchemy import select
from datetime import datetime
import asyncio

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery = Celery("tasks", broker=REDIS_URL, backend=REDIS_URL)
celery.conf.timezone = "UTC"


@celery.task(name="send_activity_notification")
def send_activity_notification(rec_state_id: int):
    """Triggered when next_rescreen_on arrives."""
    asyncio.run(_handle_activity_notification(rec_state_id))


async def _handle_activity_notification(rec_state_id: int):
    async with AsyncSessionLocal() as db:
        # Fetch the state
        result = await db.execute(
            select(RecommendationState).where(RecommendationState.id == rec_state_id)
        )
        state = result.scalar_one_or_none()
        if not state:
            print(f"[WARN] No state found for ID={rec_state_id}")
            return

        # Update attempt count + timestamp
        state.attempt_count += 1
        state.last_shown_at = datetime.utcnow()

        # Create audit record
        audit = RecommendationAudit(
            recommendation_state_id=rec_state_id,
            activity_id=state.current_activity_id,
            action="notification_sent",
            timestamp=datetime.utcnow(),
        )
        db.add(audit)

        # Get patient’s device tokens
        tokens_res = await db.execute(
            select(DeviceToken.token).where(DeviceToken.patient_id == state.patient_id)
        )
        # tokens = [r[0] for r in tokens_res.fetchall()]
        tokens = "emQ5vQUcSHmAzMrkzT1ECP:APA91bF-EpCJDrPpfjqk3bC1jc6cxjTXVAligO0cscGAYuv8diCm1gYrF6EO1bsO9cBKzfXbwdCFC4M39tvT2kxrX6FS64JWkK1YAqsNDVVpcgG7mY327vQ"

        if not tokens:
            print(f"[WARN] No device tokens for patient {state.patient_id}")
        else:
            for token in tokens:
                send_fcm_notification(
                    token=token,
                    title="Follow-up Reminder",
                    body=f"Please complete your {state.red_flag} follow-up.",
                    data={"state_id": str(state.id)},
                )
            print(f"[INFO] Sent {len(tokens)} notifications for rec_state {state.id}")

        await db.commit()


@celery.task(name="process_feedback")
def process_feedback(payload: dict):
    """Processes feedback asynchronously."""
    asyncio.run(_handle_feedback(payload))


async def _handle_feedback(payload: dict):
    async with AsyncSessionLocal() as db:
        rec_state_id = payload["recommendation_state_id"]
        feedback = payload["feedback"]
        patient_id = payload["patient_id"]

        # Record in audit table
        audit = RecommendationAudit(
            recommendation_state_id=rec_state_id,
            activity_id=payload["activity_id"],
            action=f"feedback_received: {feedback}",
            timestamp=datetime.utcnow(),
        )
        db.add(audit)

        # Optionally update state
        result = await db.execute(
            select(RecommendationState).where(RecommendationState.id == rec_state_id)
        )
        state = result.scalar_one_or_none()
        if state:
            state.last_feedback_at = datetime.utcnow()

        await db.commit()
        print(
            f"[INFO] Feedback processed for rec_state={rec_state_id}, patient={patient_id}"
        )
