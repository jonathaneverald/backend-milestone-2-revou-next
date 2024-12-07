from db import db
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy import String, Integer, DateTime
from datetime import datetime, timedelta
import bcrypt
from flask_login import UserMixin


def gmt_plus_7_now():
    return datetime.utcnow() + timedelta(hours=7)


class UserModel(db.Model, UserMixin):
    __tablename__ = "users"

    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(255), unique=False, nullable=False)
    email = mapped_column(String(255), unique=True, nullable=False)
    password = mapped_column(String(255), unique=False, nullable=False)
    profile_pict = mapped_column(String(255), unique=False, nullable=True)
    created_at = mapped_column(DateTime, default=gmt_plus_7_now, nullable=False)
    updated_at = mapped_column(DateTime, default=gmt_plus_7_now, onupdate=gmt_plus_7_now, nullable=False)

    role = relationship("RoleModel", backref="user", lazy=True)
    disabled_user = relationship("DisabledUserModel", backref="user", lazy=True, uselist=False)

    def __repr__(self):
        return f"<User {self.id}>"

    def to_dictionaries(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "profile_pict": self.profile_pict,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def set_password(self, password):
        self.password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def check_password(self, password):
        return bcrypt.checkpw(password.encode("utf-8"), self.password.encode("utf-8"))
