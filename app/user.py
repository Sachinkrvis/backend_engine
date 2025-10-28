from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app import crud, schemas
import logging

logger = logging.getLogger("user")
router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/api/login", response_model=schemas.PatientOut)
async def login_user(payload: schemas.PatientIn, db: AsyncSession = Depends(get_db)):
    """
    Dev login: fetch patient by username+email, create if not exists
    """
    existing = await crud.get_patient_by_username_email(db, payload.username, payload.email)
    if existing:
        logger.info(f"Existing patient login: {existing.patient_id}")
        return existing

    patient = await crud.create_patient(db, payload.username, payload.email)
    logger.info(f"Created new patient: {patient.patient_id}")
    return patient
