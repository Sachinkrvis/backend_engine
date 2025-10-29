# app/crud.py

from datetime import datetime, timedelta
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.models import RecommendationState, FeedbackEvent, DeviceToken, Activity
from app.notifications import send_fcm_notification


# -----------------------------------------------------------
# Create recommendation state from red_flag lookup
# -----------------------------------------------------------
async def create_recommendation_state_from_redflag(
    db: AsyncSession,
    child_id: int,
    parent_id: int,
    patient_id: str | None,
    pediatrician_id: int | None,
    red_flag: str,
):
    """
    1. Look up activity for given red_flag (lowest step_order)
    2. Create a new RecommendationState record
    3. Insert corresponding RecommendationAudit entry
    """
    from app.models import Activity, RecommendationState, RecommendationAudit

    # 1️⃣ Get the first activity for the red_flag (step_order = 1)
    result = await db.execute(
        select(Activity)
        .where(Activity.red_flag == red_flag)
        .order_by(Activity.step_order.asc())
        .limit(1)
    )
    activity = result.scalar_one_or_none()
    if not activity:
        raise ValueError(f"No activity found for red_flag={red_flag}")

    # 2️⃣ Create RecommendationState
    state = RecommendationState(
        child_id=child_id,
        parent_id=parent_id,
        patient_id=patient_id,
        pediatrician_id=pediatrician_id,
        red_flag=red_flag,
        current_activity_id=activity.activity_id,
        current_step_order=activity.step_order,
        next_rescreen_on=None,
    )
    db.add(state)
    await db.flush()  # Get state.id before commit

    # 3️⃣ Create RecommendationAudit (log)
    audit = RecommendationAudit(
        recommendation_state_id=state.id,
        child_id=child_id,
        patient_id=patient_id,
        parent_id=parent_id,
        pediatrician_id=pediatrician_id,
        red_flag=red_flag,
        activity_id=activity.activity_id,
        rendered_card={
            "content": activity.content_jsonb,
            "duration_days": activity.duration_days,
            "duration_minutes": activity.duration_minutes,
            "sequence_order": activity.step_order,
        },
        ruleset_version=activity.version,
    )
    db.add(audit)

    await db.commit()
    await db.refresh(state)
    # 4️⃣ Fetch parent’s FCM token
    # tokens_result = await db.execute(
    #     select(DeviceToken.token).where(DeviceToken.patient_id == parent_id)
    # )
    # tokens = [r[0] for r in tokens_result.fetchall()]
    # token = "ed3I12hJSsWplE5xiRP---:APA91bEP-CqvVVfGTPea2tMgqei3P5vA8cHXVq_wjadH8BBwOXhP94-4ydlzNt_qviWYQkqh5LQVBXU2Mzqh-q-a2Mm7Y6nj-rQ9VMFV4YPxnm_NW6PAVI4"
    token = "fAUx-xAyQ32h8w-ULcx-BF:APA91bGHLNLR3_x_RLaFUtyCvZjIcKfEEHGZpkAdwenECJf6W_6LF_dY2bLs1C3ObrtNPebki-9qr6wSxd3pyTkU_Pvb7VeNG3XIZhH7U_sR_Iul4APbIdI"
    send_fcm_notification(
        token=token,
        title="Red Flag Detected",
        body=f"A new red flag was detected: {red_flag}",
        data={"child_id": str(child_id), "red_flag": red_flag},
    )
    # 5️⃣ Send notification directly
    # if not tokens:
    #     print(f"[WARN] No FCM tokens found for parent_id={parent_id}")
    # else:
    #     for token in tokens:
    #         send_fcm_notification(
    #             token=token,
    #             title="Red Flag Detected",
    #             body=f"A new red flag was detected: {red_flag}",
    #             data={"child_id": str(child_id), "red_flag": red_flag},
    #         )
    #         print(f"[INFO] Notification sent to parent {parent_id}")
    return state


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
