from sqlalchemy import Column, Integer, String, Text, Boolean
from database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)  # ✅ email requis pour vérification
    full_name = Column(String)  # ✅ nom complet
    hashed_password = Column(String)
    role = Column(String)
    permissions = Column(String, nullable=True)  # ✅ autorise None

    is_verified = Column(Boolean, default=False)  # ✅ vérification email
    verification_code = Column(String, nullable=True)
    verification_sent_at = Column(String, nullable=True)  # ⏳ horodatage du code

    @property
    def permissions_list(self):
        return self.permissions.split(",") if self.permissions else []

class AdminLog(Base):
    __tablename__ = "admin_logs"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)  # ex: "delete_user", "verify_user"
    target_user_id = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(String, nullable=True)