from db import db
from sqlalchemy.orm import mapped_column
from sqlalchemy import String, Integer, DateTime, Text, ForeignKey
from datetime import datetime, timedelta


def gmt_plus_7_now():
    return datetime.utcnow() + timedelta(hours=7)


class DisabledUserModel(db.Model):
    __tablename__ = "disabled_users"

    id = mapped_column(Integer, ForeignKey("users.id"), primary_key=True, nullable=False)
    accessibility_preferences = mapped_column(Text, nullable=False)
    disability_type = mapped_column(String(255), nullable=False)
    created_at = mapped_column(DateTime, default=gmt_plus_7_now, nullable=False)
    updated_at = mapped_column(DateTime, default=gmt_plus_7_now, onupdate=gmt_plus_7_now, nullable=False)

    def __repr__(self):
        return f"<Disabled User {self.id}>"

    def to_dictionaries(self):
        return {
            "id": self.id,
            "accessibility_preferences": self.accessibility_preferences,
            "disability_type": self.disability_type,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
