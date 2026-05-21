import json
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator

from app.database import Base


class JSONType(TypeDecorator):
    """Store Python dicts as JSON strings in SQLite."""

    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value, ensure_ascii=False)
        return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return None


class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    subject_template = Column(Text, nullable=False)
    body_template = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())

    campaigns = relationship("Campaign", back_populates="template")


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=False)
    status = Column(String, nullable=False, default="draft")
    send_start = Column(DateTime, nullable=True)
    send_end = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())

    template = relationship("Template", back_populates="campaigns")
    emails = relationship("CampaignEmail", back_populates="campaign")


class CampaignEmail(Base):
    __tablename__ = "campaign_emails"

    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    recipient_email = Column(String, nullable=False)
    recipient_data = Column(JSONType, nullable=False)
    rendered_subject = Column(Text, nullable=False)
    rendered_body = Column(Text, nullable=False)
    scheduled_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    send_status = Column(String, nullable=False, default="pending")
    failure_reason = Column(Text, nullable=True)
    tracking_id = Column(String, unique=True, nullable=False)
    gmail_message_id = Column(String, nullable=True)
    opened_at = Column(DateTime, nullable=True)
    reply_detected_at = Column(DateTime, nullable=True)

    campaign = relationship("Campaign", back_populates="emails")
    follow_ups = relationship("FollowUp", back_populates="campaign_email")


class FollowUp(Base):
    __tablename__ = "follow_ups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_email_id = Column(
        Integer, ForeignKey("campaign_emails.id"), nullable=False
    )
    note = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())

    campaign_email = relationship("CampaignEmail", back_populates="follow_ups")
