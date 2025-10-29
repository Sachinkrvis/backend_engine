# app/main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app import crud, schemas
from app.tasks import send_activity_notification, process_feedback
import logging
from datetime import datetime, timezone

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("app")

app = FastAPI(title="Red Flag Recommendation API")


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@app.post("/api/redflag", response_model=schemas.RecommendationStateOut)
async def create_redflag(
    payload: schemas.CreateRedFlag, db: AsyncSession = Depends(get_db)
):
    logger.info(
        f"Received new redflag for patient={payload.patient_id}, red_flag={payload.red_flag}"
    )

    try:
        rec = await crud.create_recommendation_state_from_redflag(
            db=db,
            child_id=payload.child_id,
            parent_id=payload.parent_id,
            patient_id=payload.patient_id,
            pediatrician_id=payload.pediatrician_id,
            red_flag=payload.red_flag,
        )

        logger.info(
            f"✅ Created RecommendationState id={rec.id} for {payload.red_flag}"
        )
        return rec

    except ValueError as e:
        logger.error(str(e))
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception("Failed to create recommendation state")
        raise HTTPException(status_code=500, detail=str(e))


# @app.post("/api/redflag", response_model=schemas.RecommendationStateOut)
# async def create_redflag(
#     payload: schemas.CreateRedFlag, db: AsyncSession = Depends(get_db)
# ):
#     logger.info(
#         f"Received new redflag for patient {payload.patient_id} ({payload.red_flag})"
#     )

#     next_rescreen = payload.next_rescreen_on
#     rec = await crud.create_recommendation_state(
#         db,
#         payload.patient_id,
#         payload.red_flag,
#         payload.current_activity_id,
#         payload.current_step_order,
#         next_rescreen,
#     )

#     if not rec:
#         existing = await crud.get_state(db, payload.patient_id, payload.red_flag)
#         if not existing:
#             raise HTTPException(
#                 status_code=500, detail="Failed to create/retrieve state"
#             )
#         rec = existing

#     # 🧠 Schedule background notification task
#     if next_rescreen:
#         eta_time = datetime.fromisoformat(str(next_rescreen)).replace(
#             tzinfo=timezone.utc
#         )
#         send_activity_notification.apply_async(args=[rec.id], eta=eta_time)
#         logger.info(f"Scheduled notification for {eta_time} (state_id={rec.id})")
#     else:
#         logger.warning("next_rescreen_on missing — task not scheduled")

#     return rec


@app.post("/api/feedback")
async def post_feedback(event: schemas.FeedbackIn, db: AsyncSession = Depends(get_db)):
    logger.info(f"Feedback received for rec_state={event.recommendation_state_id}")
    # enqueue background feedback processor
    process_feedback.delay(event.dict())
    return {"ok": True}


@app.post("/api/device-token")
async def add_device_token(
    token: schemas.DeviceTokenIn, db: AsyncSession = Depends(get_db)
):
    dt = await crud.add_device_token(db, token.patient_id, token.token, token.platform)
    return {"ok": True, "id": dt.id}


@app.get(
    "/api/state/{patient_id}/{red_flag}", response_model=schemas.RecommendationStateOut
)
async def get_state(patient_id: int, red_flag: str, db: AsyncSession = Depends(get_db)):
    s = await crud.get_state(db, patient_id, red_flag)
    if not s:
        raise HTTPException(status_code=404, detail="Not found")
    return s
