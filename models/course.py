from db import db
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text
from datetime import datetime, timedelta


def gmt_plus_7_now():
    return datetime.utcnow() + timedelta(hours=7)


class CourseModel(db.Model):
    __tablename__ = "courses"

    id = mapped_column(Integer, primary_key=True)
    institute_id = mapped_column(Integer, ForeignKey("institutes.id"), unique=False, nullable=False)
    role_id = mapped_column(Integer, ForeignKey("roles.id"), unique=False, nullable=False)
    title = mapped_column(String(255), unique=False, nullable=False)
    description = mapped_column(Text, unique=False, nullable=False)
    category = mapped_column(String(255), unique=False, nullable=False)
    media = mapped_column(String(255), unique=False, nullable=False)  # this column is to store url of the media
    created_at = mapped_column(DateTime, default=gmt_plus_7_now, nullable=False)
    updated_at = mapped_column(DateTime, default=gmt_plus_7_now, onupdate=gmt_plus_7_now, nullable=False)

    module = relationship("ModuleModel", backref="course", lazy=True)
    enrollment = relationship("EnrollmentModel", backref="course", lazy=True)

    def __repr__(self):
        return f"<Course {self.id}>"

    def to_dictionaries(self):
        return {
            "id": self.id,
            "institute_id": self.institute_id,
            "role_id": self.role_id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "media": self.media,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
