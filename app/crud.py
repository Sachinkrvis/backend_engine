# app/crud.py

from datetime import datetime, timedelta
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.models import RecommendationState, FeedbackEvent, DeviceToken, Activity


# -----------------------------------------------------------
# Create recommendation state (insert or ignore on conflict)
# -----------------------------------------------------------
async def create_recommendation_state(
    db: AsyncSession,
    patient_id: int,
    red_flag: str,
    activity_id: str | None = None,
    step_order: int = 1,
    next_rescreen_on: datetime | None = None,
):
    """
    Creates a recommendation state for a patient-red_flag pair.
    If it already exists, do nothing (PostgreSQL ON CONFLICT DO NOTHING).
    """

    stmt = (
        insert(RecommendationState)
        .values(
            patient_id=patient_id,
            red_flag=red_flag,
            current_activity_id=activity_id,
            current_step_order=step_order,
            next_rescreen_on=next_rescreen_on,
        )
        .on_conflict_do_nothing(index_elements=["patient_id", "red_flag"])
        .returning(RecommendationState.id)
    )

    result = await db.execute(stmt)
    await db.commit()

    # Fetch and return the existing or newly inserted record
    q = await db.execute(
        select(RecommendationState).where(
            RecommendationState.patient_id == patient_id,
            RecommendationState.red_flag == red_flag,
        )
    )
    return q.scalar_one_or_none()


# -----------------------------------------------------------
# Get current recommendation state
# -----------------------------------------------------------
async def get_state(db: AsyncSession, patient_id: int, red_flag: str):
    """
    Retrieve the current recommendation state for a given patient and red_flag.
    """
    q = await db.execute(
        select(RecommendationState).where(
            RecommendationState.patient_id == patient_id,
            RecommendationState.red_flag == red_flag,
        )
    )
    return q.scalar_one_or_none()


# -----------------------------------------------------------
# Insert feedback and optionally update recommendation state
# -----------------------------------------------------------
async def insert_feedback(
    db: AsyncSession,
    rec_state_id: int,
    patient_id: int,
    activity_id: str,
    feedback: str,
    notes: str | None = None,
):
    """
    Insert feedback for a recommendation state.
    If feedback == 'done', mark the recommendation as resolved.
    """

    ev = FeedbackEvent(
        recommendation_state_id=rec_state_id,
        patient_id=patient_id,
        activity_id=activity_id,
        feedback=feedback,
        notes=notes,
    )
    db.add(ev)

    # Example: mark the recommendation as resolved if done
    if feedback.lower() == "done":
        await db.execute(
            update(RecommendationState)
            .where(RecommendationState.id == rec_state_id)
            .values(status="resolved")
        )

    await db.commit()
    return ev


# -----------------------------------------------------------
# Add new device token for push notifications
# -----------------------------------------------------------
async def add_device_token(
    db: AsyncSession, patient_id: int, token: str, platform: str | None = None
):
    """
    Store a device token for a patient (used for FCM notifications).
    """
    dt = DeviceToken(patient_id=patient_id, token=token, platform=platform)
    db.add(dt)
    await db.commit()
    return dt
