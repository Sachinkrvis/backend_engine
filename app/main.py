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
        f"Received new redflag for patient {payload.patient_id} ({payload.red_flag})"
    )

    next_rescreen = payload.next_rescreen_on
    rec = await crud.create_recommendation_state(
        db,
        payload.patient_id,
        payload.red_flag,
        payload.current_activity_id,
        payload.current_step_order,
        next_rescreen,
    )

    if not rec:
        existing = await crud.get_state(db, payload.patient_id, payload.red_flag)
        if not existing:
            raise HTTPException(
                status_code=500, detail="Failed to create/retrieve state"
            )
        rec = existing

    # 🧠 Schedule background notification task
    if next_rescreen:
        eta_time = datetime.fromisoformat(str(next_rescreen)).replace(
            tzinfo=timezone.utc
        )
        send_activity_notification.apply_async(args=[rec.id], eta=eta_time)
        logger.info(f"Scheduled notification for {eta_time} (state_id={rec.id})")
    else:
        logger.warning("next_rescreen_on missing — task not scheduled")

    return rec


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


# # app/main.py
# from fastapi import FastAPI, Depends, HTTPException
# from sqlalchemy.ext.asyncio import AsyncSession
# from app.database import AsyncSessionLocal
# from app import crud, schemas
# import logging

# logging.basicConfig(
#     level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
# )
# logger = logging.getLogger("app")


# app = FastAPI(title="Red Flag Recommendation API")


# async def get_db():
#     async with AsyncSessionLocal() as session:
#         yield session


# @app.post("/api/redflag", response_model=schemas.RecommendationStateOut)
# async def create_redflag(
#     payload: schemas.CreateRedFlag, db: AsyncSession = Depends(get_db)
# ):
#     # Insert-time flow: create recommendation_state (ON CONFLICT DO NOTHING)
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
#         logger.warning(
#             "Recommendation state already exists or creation failed. Fetching existing..."
#         )
#         # return existing
#         existing = await crud.get_state(db, payload.patient_id, payload.red_flag)
#         if not existing:
#             logger.error("Failed to create or retrieve state!")
#             raise HTTPException(
#                 status_code=500, detail="Failed to create/retrieve state"
#             )
#         return existing
#     logger.info(f"Created recommendation state ID={rec.id}")
#     return rec


# @app.post("/api/feedback")
# async def post_feedback(event: schemas.FeedbackIn, db: AsyncSession = Depends(get_db)):
#     logger.info(
#         f"Feedback received for rec_state={event.recommendation_state_id}, patient={event.patient_id}, feedback={event.feedback}"
#     )
#     ev = await crud.insert_feedback(
#         db,
#         event.recommendation_state_id,
#         event.patient_id,
#         event.activity_id,
#         event.feedback,
#         event.notes,
#     )
#     logger.info(f"Feedback inserted successfully with ID={ev.id}")
#     return {"ok": True, "id": ev.id}


# @app.post("/api/device-token")
# async def add_device_token(
#     token: schemas.DeviceTokenIn, db: AsyncSession = Depends(get_db)
# ):
#     logger.info(f"Adding device token for patient {token.patient_id}")
#     dt = await crud.add_device_token(db, token.patient_id, token.token, token.platform)
#     logger.info(f"Device token added ID={dt.id}")
#     return {"ok": True, "id": dt.id}


# @app.get(
#     "/api/state/{patient_id}/{red_flag}", response_model=schemas.RecommendationStateOut
# )
# async def get_state(patient_id: int, red_flag: str, db: AsyncSession = Depends(get_db)):
#     s = await crud.get_state(db, patient_id, red_flag)
#     if not s:
#         raise HTTPException(status_code=404, detail="Not found")
#     return s
