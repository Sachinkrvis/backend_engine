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
    ForeignKey,
    Boolean,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Base(DeclarativeBase):
    pass


# -----------------------
# Activity Table
# -----------------------
class Activity(Base):
    __tablename__ = "activities"
    activity_id = Column(String, primary_key=True)
    red_flag = Column(String, nullable=False, index=True)
    step_order = Column(Integer, nullable=False)
    duration_days = Column(Integer, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    content_jsonb = Column(JSON, nullable=False)  # raw activity desc,material,video_url
    alternatives = Column(ARRAY(Text), default=[])
    version = Column(String, default="v1.0")
    created_by = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    __table_args__ = (
        UniqueConstraint("red_flag", "step_order", name="ux_activities_redflag_step"),
    )


# -----------------------
# Recommendation State
# -----------------------
class RecommendationState(Base):
    __tablename__ = "recommendation_state"
    id = Column(Integer, primary_key=True, autoincrement=True)
    child_id = Column(Integer, nullable=False, index=True)
    patient_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    parent_id = Column(Integer, nullable=False)
    pediatrician_id = Column(Integer, nullable=True)
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
        UniqueConstraint(
            "child_id", "parent_id", "red_flag", name="ux_state_child_parent_redflag"
        ),
    )


# -----------------------
# Recommendation Audit
# -----------------------
class RecommendationAudit(Base):
    __tablename__ = "recommendation_audit"
    id = Column(Integer, primary_key=True, autoincrement=True)
    recommendation_state_id = Column(Integer)
    child_id = Column(Integer, nullable=False)
    patient_id = Column(UUID(as_uuid=True))
    parent_id = Column(Integer, nullable=False)
    pediatrician_id = Column(Integer, nullable=True)
    red_flag = Column(String)
    activity_id = Column(String)
    rendered_card = Column(JSON)  # AI generated message
    ruleset_version = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


# -----------------------
# Feedback Event
# -----------------------
class FeedbackEvent(Base):
    __tablename__ = "feedback_events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    recommendation_state_id = Column(Integer, nullable=False)
    child_id = Column(Integer, nullable=False)
    patient_id = Column(UUID(as_uuid=True), nullable=True)
    parent_id = Column(Integer, nullable=False)
    pediatrician_id = Column(Integer, nullable=True)
    activity_id = Column(String)
    feedback = Column(String, nullable=False)  # 'done'|'too_hard'|'skip'...
    notes = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


# -----------------------
# Device Token
# -----------------------
class DeviceToken(Base):
    __tablename__ = "device_tokens"
    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(Integer, nullable=True, index=True)
    pediatrician_id = Column(Integer, nullable=True)
    token = Column(String, nullable=False)
    platform = Column(String)
    isActive = Column(Boolean)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


# -----------------------
# Scheduled Jobs
# -----------------------
class ScheduledJob(Base):
    __tablename__ = "scheduled_jobs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    recommendation_state_id = Column(Integer)
    job_type = Column(String, nullable=False)
    due_at = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    status = Column(String, default="queued")
    attempt = Column(Integer, default=0)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


# -----------------------
# Final Outcomes
# -----------------------
class FinalOutcome(Base):
    __tablename__ = "final_outcomes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    child_id = Column(Integer, nullable=False)
    patient_id = Column(UUID(as_uuid=True), nullable=True)
    parent_id = Column(Integer, nullable=False)
    pediatrician_id = Column(Integer, nullable=True)  # pediatrician_id
    red_flag = Column(String, nullable=False)
    total_activities_notified = Column(Integer, default=0)
    total_feedback_events = Column(Integer, default=0)
    status = Column(
        String, nullable=False, default="open"
    )  # 'open'|'resolved'|'escalated'|'not_resolved'
    resolution_method = Column(
        String
    )  # 'feedback_done'|'auto_resolved'|'not_resolved_after_all'|'doctor_closed'
    resolved_at = Column(TIMESTAMP(timezone=True))
    last_feedback_event_id = Column(
        Integer, ForeignKey("feedback_events.id", ondelete="SET NULL")
    )
    notes = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    __table_args__ = (
        UniqueConstraint(
            "child_id",
            "parent_id",
            "red_flag",
            name="ux_finaloutcome_parent_child_redflag",
        ),
    )
