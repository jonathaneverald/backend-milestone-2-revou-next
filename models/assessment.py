from db import db
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy import Integer, DateTime, ForeignKey, Enum
from datetime import datetime, timedelta
from enums.enum import AssesmentTypeEnum


def gmt_plus_7_now():
    return datetime.utcnow() + timedelta(hours=7)


class AssessmentModel(db.Model):
    __tablename__ = "assessments"

    id = mapped_column(Integer, primary_key=True)
    module_id = mapped_column(Integer, ForeignKey("modules.id"), unique=False, nullable=False)
    type = mapped_column(Enum(AssesmentTypeEnum), default=AssesmentTypeEnum.choices, unique=False, nullable=False)
    created_at = mapped_column(DateTime, default=gmt_plus_7_now, nullable=False)
    updated_at = mapped_column(DateTime, default=gmt_plus_7_now, onupdate=gmt_plus_7_now, nullable=False)

    assessment_detail = relationship("AssessmentDetailModel", backref="assessment", lazy=True, uselist=False)
    submission = relationship("SubmissionModel", backref="assessment", lazy=True)

    def __repr__(self):
        return f"<Assessment {self.id}>"

    def to_dictionaries(self):
        return {
            "id": self.id,
            "module_id": self.module_id,
            "type": self.type,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
