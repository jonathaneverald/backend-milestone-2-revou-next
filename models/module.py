from db import db
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text
from datetime import datetime, timedelta


def gmt_plus_7_now():
    return datetime.utcnow() + timedelta(hours=7)


class ModuleModel(db.Model):
    __tablename__ = "modules"

    id = mapped_column(Integer, primary_key=True)
    course_id = mapped_column(Integer, ForeignKey("courses.id"), unique=False, nullable=False)
    title = mapped_column(String(255), unique=False, nullable=False)
    content = mapped_column(Text, unique=False, nullable=False)
    module_file = mapped_column(String(255), unique=False, nullable=True)  # to store url file (optional)
    created_at = mapped_column(DateTime, default=gmt_plus_7_now, nullable=False)
    updated_at = mapped_column(DateTime, default=gmt_plus_7_now, onupdate=gmt_plus_7_now, nullable=False)

    assessment = relationship("AssessmentModel", backref="module", lazy=True)

    def __repr__(self):
        return f"<Module {self.id}>"

    def to_dictionaries(self):
        return {
            "id": self.id,
            "course_id": self.course_id,
            "title": self.title,
            "content": self.content,
            "module_file": self.module_file,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
