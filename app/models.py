# app/models.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    JSON,
    TIMESTAMP,
    ARRAY,
    func,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.sql import expression
from sqlalchemy.sql.sqltypes import Boolean


class Base(DeclarativeBase):
    pass


class Activity(Base):
    __tablename__ = "activities"
    activity_id = Column(String, primary_key=True)
    red_flag = Column(String, nullable=False, index=True)
    step_order = Column(Integer, nullable=False)
    level = Column(String, nullable=False)
    duration_days = Column(Integer, nullable=False)
    content_jsonb = Column(JSON, nullable=False)
    alternatives = Column(ARRAY(Text), default=[])
    version = Column(String, default="v1.0")
    created_by = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("red_flag", "step_order", name="ux_activities_redflag_step"),
    )


class RecommendationState(Base):
    __tablename__ = "recommendation_state"
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, nullable=False, index=True)
    red_flag = Column(String, nullable=False)
    status = Column(String, nullable=False, default="active")
    current_activity_id = Column(String)
    current_step_order = Column(Integer)
    attempt_count = Column(Integer, default=0)
    total_attempts = Column(Integer, default=0)
    last_shown_at = Column(TIMESTAMP(timezone=True))
    next_rescreen_on = Column(TIMESTAMP(timezone=True), index=True)
    skip_count = Column(Integer, default=0)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("patient_id", "red_flag", name="ux_state_patient_redflag"),
    )


class FeedbackEvent(Base):
    __tablename__ = "feedback_events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    recommendation_state_id = Column(Integer, nullable=False)
    patient_id = Column(Integer, nullable=False)
    activity_id = Column(String)
    feedback = Column(String, nullable=False)  # 'done'|'too_hard'|'skip'...
    notes = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class RecommendationAudit(Base):
    __tablename__ = "recommendation_audit"
    id = Column(Integer, primary_key=True, autoincrement=True)
    recommendation_state_id = Column(Integer)
    patient_id = Column(Integer)
    red_flag = Column(String)
    activity_id = Column(String)
    rendered_card = Column(JSON)
    ruleset_version = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class DeviceToken(Base):
    __tablename__ = "device_tokens"
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, index=True)
    token = Column(String, nullable=False)
    platform = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class ScheduledJob(Base):
    __tablename__ = "scheduled_jobs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    recommendation_state_id = Column(Integer)
    job_type = Column(String, nullable=False)
    due_at = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    status = Column(String, default="queued")
    attempt = Column(Integer, default=0)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
