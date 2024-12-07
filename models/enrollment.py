from db import db
from sqlalchemy.orm import mapped_column
from sqlalchemy import Integer, DateTime, ForeignKey, Enum
from datetime import datetime, timedelta
from enums.enum import EnrollStatusEnum


def gmt_plus_7_now():
    return datetime.utcnow() + timedelta(hours=7)


class EnrollmentModel(db.Model):
    __tablename__ = "enrollments"

    id = mapped_column(Integer, primary_key=True)
    role_id = mapped_column(Integer, ForeignKey("roles.id"), unique=False, nullable=False)
    course_id = mapped_column(Integer, ForeignKey("courses.id"), unique=False, nullable=False)
    enrolled_at = mapped_column(DateTime, unique=False, nullable=False)
    status = mapped_column(Enum(EnrollStatusEnum), default=EnrollStatusEnum.pending, unique=False, nullable=False)
    created_at = mapped_column(DateTime, default=gmt_plus_7_now, nullable=False)
    updated_at = mapped_column(DateTime, default=gmt_plus_7_now, onupdate=gmt_plus_7_now, nullable=False)

    def __repr__(self):
        return f"<Enrollment {self.id}>"

    def to_dictionaries(self):
        return {
            "id": self.id,
            "role_id": self.role_id,
            "course_id": self.course_id,
            "enrolled_at": self.enrolled_at,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
