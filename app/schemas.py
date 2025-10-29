# app/schemas.py
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime
from uuid import UUID


class CreateRedFlag(BaseModel):
    child_id: int
    parent_id: int
    patient_id: UUID
    pediatrician_id: Optional[int] = None
    red_flag: str


class FeedbackIn(BaseModel):
    recommendation_state_id: int
    patient_id: UUID  # <-- FIXED to UUID
    activity_id: Optional[str]
    feedback: str
    notes: Optional[str]


class DeviceTokenIn(BaseModel):
    patient_id: UUID  # <-- FIXED to UUID
    token: str
    platform: Optional[str]


class RecommendationStateOut(BaseModel):
    id: int
    patient_id: UUID  # <-- FIXED to UUID
    red_flag: str
    status: str
    current_activity_id: Optional[str]
    current_step_order: Optional[int]
    next_rescreen_on: Optional[datetime]

    class Config:
        from_attributes = True


# # app/schemas.py
# from pydantic import BaseModel
# from typing import Optional, Any
# from datetime import datetime
# from uuid import UUID


# class CreateRedFlag(BaseModel):
#     child_id: int
#     parent_id: int
#     patient_id: UUID
#     pediatrician_id: Optional[int] = None
#     red_flag: str


# # class CreateRedFlag(BaseModel):
# #     patient_id: int
# #     red_flag: str
# #     current_activity_id: Optional[str] = None
# #     current_step_order: Optional[int] = 1
# #     next_rescreen_on: Optional[datetime] = None


# class FeedbackIn(BaseModel):
#     recommendation_state_id: int
#     patient_id: int
#     activity_id: Optional[str]
#     feedback: str
#     notes: Optional[str]


# class DeviceTokenIn(BaseModel):
#     patient_id: int
#     token: str
#     platform: Optional[str]


# class RecommendationStateOut(BaseModel):
#     id: int
#     patient_id: int
#     red_flag: str
#     status: str
#     current_activity_id: Optional[str]
#     current_step_order: Optional[int]
#     next_rescreen_on: Optional[datetime]

#     class Config:
#         from_attributes = True
