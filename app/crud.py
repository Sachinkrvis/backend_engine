# app/crud.py
from sqlalchemy import select, and_, update, insert
from sqlalchemy.exc import IntegrityError
from app.models import RecommendationState, FeedbackEvent, DeviceToken, Activity
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta


async def create_recommendation_state(
    db: AsyncSession,
    patient_id: int,
    red_flag: str,
    activity_id=None,
    step_order=1,
    next_rescreen_on=None,
):
    stmt = (
        insert(RecommendationState)
        .values(
            patient_id=patient_id,
            red_flag=red_flag,
            current_activity_id=activity_id,
            current_step_order=step_order,
            next_rescreen_on=next_rescreen_on,
        )
        .prefix_with("ON CONFLICT (patient_id, red_flag) DO NOTHING")
    )
    await db.execute(stmt)
    await db.commit()
    # fetch and return
    q = await db.execute(
        select(RecommendationState).where(
            RecommendationState.patient_id == patient_id,
            RecommendationState.red_flag == red_flag,
        )
    )
    return q.scalar_one_or_none()


async def get_state(db: AsyncSession, patient_id: int, red_flag: str):
    q = await db.execute(
        select(RecommendationState).where(
            RecommendationState.patient_id == patient_id,
            RecommendationState.red_flag == red_flag,
        )
    )
    return q.scalar_one_or_none()


async def insert_feedback(
    db: AsyncSession,
    rec_state_id: int,
    patient_id: int,
    activity_id: str,
    feedback: str,
    notes: str | None,
):
    ev = FeedbackEvent(
        recommendation_state_id=rec_state_id,
        patient_id=patient_id,
        activity_id=activity_id,
        feedback=feedback,
        notes=notes,
    )
    db.add(ev)
    # example transaction: if feedback == 'done' mark state resolved
    if feedback == "done":
        await db.execute(
            update(RecommendationState)
            .where(RecommendationState.id == rec_state_id)
            .values(status="resolved")
        )
    await db.commit()
    return ev


async def add_device_token(
    db: AsyncSession, patient_id: int, token: str, platform: str | None
):
    dt = DeviceToken(patient_id=patient_id, token=token, platform=platform)
    db.add(dt)
    await db.commit()
    return dt
