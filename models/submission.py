from db import db
from sqlalchemy.orm import mapped_column
from sqlalchemy import Integer, DateTime, ForeignKey, String, JSON
from datetime import datetime, timedelta


def gmt_plus_7_now():
    return datetime.utcnow() + timedelta(hours=7)


class SubmissionModel(db.Model):
    __tablename__ = "submissions"

    id = mapped_column(Integer, primary_key=True)
    assessment_id = mapped_column(Integer, ForeignKey("assessments.id"), unique=False, nullable=False)
    role_id = mapped_column(Integer, ForeignKey("roles.id"), unique=False, nullable=False)
    score = mapped_column(
        Integer, unique=False, nullable=True
    )  # to store score, automatically generated if the assessment type is multiple choices
    answer = mapped_column(
        JSON, unique=False, nullable=True
    )
    file = mapped_column(String(255), unique=False, nullable=True)
    submitted_at = mapped_column(DateTime, default=gmt_plus_7_now, nullable=False)
    updated_at = mapped_column(DateTime, default=gmt_plus_7_now, onupdate=gmt_plus_7_now, nullable=False)

    def __repr__(self):
        return f"<Submission {self.id}>"

    def to_dictionaries(self):
        return {
            "id": self.id,
            "assessment_id": self.assessment_id,
            "role_id": self.role_id,
            "score": self.score,
            "answer": self.answer,
            "file": self.file,
            "submitted_at": self.submitted_at,
            "updated_at": self.updated_at,
        }
