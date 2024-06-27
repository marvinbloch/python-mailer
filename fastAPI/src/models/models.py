from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..config.database import Base

class Email(Base):
    __tablename__ = "email"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    email = Column(String, unique=True, index=True)
    active = Column(Boolean, default=True)
    valid = Column(Boolean, default=False)
    reachable = Column(Boolean, default=False)
    history = relationship("EmailHistory", back_populates="email")


class EmailHistory(Base):
    __tablename__ = "email_history"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Integer, ForeignKey('email.id'), nullable=False)
    send_at = Column(DateTime(timezone=True), server_default=func.now())
    tracking_id = Column(String, unique=True, index=True)
    redirect_url = Column(String)
    click_count = Column(Integer, default=0)
    success = Column(Boolean, default=True)
    email = relationship("Email", back_populates="history")


class ConnectionLog(Base):
    __tablename__ = "connection_log"

    id = Column(Integer, primary_key=True, index=True)
    tracking_id = Column(String, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    origin = Column(String)
    user_agent = Column(String)
    referer = Column(String)
    path = Column(String)
    query_params = Column(String)
    status_code = Column(Integer)
    response_time = Column(Integer)
    message = Column(String)

    
    
