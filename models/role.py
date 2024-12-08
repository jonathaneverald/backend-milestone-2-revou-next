from db import db
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy import Integer, DateTime, ForeignKey, Enum
from datetime import datetime, timedelta
from enums.enum import UserRoleEnum, RoleStatusEnum


def gmt_plus_7_now():
    return datetime.utcnow() + timedelta(hours=7)


class RoleModel(db.Model):
    __tablename__ = "roles"

    id = mapped_column(Integer, primary_key=True)
    institute_id = mapped_column(Integer, ForeignKey("institutes.id"), unique=False, nullable=False)
    user_id = mapped_column(Integer, ForeignKey("users.id"), unique=False, nullable=False)
    role = mapped_column(Enum(UserRoleEnum), default=UserRoleEnum.admin, unique=False, nullable=False)
    status = mapped_column(Enum(RoleStatusEnum), default=RoleStatusEnum.pending, unique=False, nullable=False)
    created_at = mapped_column(DateTime, default=gmt_plus_7_now, nullable=False)
    updated_at = mapped_column(DateTime, default=gmt_plus_7_now, onupdate=gmt_plus_7_now, nullable=False)

    submission = relationship("SubmissionModel", backref="role", lazy=True)
    enrollment = relationship("EnrollmentModel", backref="role", lazy=True)
    course = relationship("CourseModel", backref="role", lazy=True)

    def __repr__(self):
        return f"<Role {self.id}>"

    def to_dictionaries(self):
        return {
            "id": self.id,
            "institute_id": self.institute_id,
            "user_id": self.user_id,
            "role": self.role,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
