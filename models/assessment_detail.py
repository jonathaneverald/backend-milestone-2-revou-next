from db import db
from sqlalchemy.orm import mapped_column
from sqlalchemy import Integer, DateTime, ForeignKey, String, JSON
from datetime import datetime, timedelta


def gmt_plus_7_now():
    return datetime.utcnow() + timedelta(hours=7)


class AssessmentDetailModel(db.Model):
    __tablename__ = "assessment_details"

    id = mapped_column(Integer, primary_key=True)
    assessment_id = mapped_column(Integer, ForeignKey("assessments.id"), unique=False, nullable=False)
    title = mapped_column(String(255), unique=False, nullable=False)
    question = mapped_column(JSON, unique=False, nullable=False)
    answer = mapped_column(
        JSON, unique=False, nullable=True
    )  # store the answer if the assessment type is multiple-choice
    deadline = mapped_column(DateTime, nullable=False)
    created_at = mapped_column(DateTime, default=gmt_plus_7_now, nullable=False)
    updated_at = mapped_column(DateTime, default=gmt_plus_7_now, onupdate=gmt_plus_7_now, nullable=False)

    def __repr__(self):
        return f"<Assessment Detail {self.id}>"

    def to_dictionaries(self):
        return {
            "id": self.id,
            "assessment_id": self.assessment_id,
            "title": self.title,
            "question": self.question,
            "answer": self.answer,
            "deadline": self.deadline,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
