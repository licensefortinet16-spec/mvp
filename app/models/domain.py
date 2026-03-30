from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.sql import func
from app.core.db import Base

class Tenant(Base):
    __tablename__ = "tenants"

    # No MVP, o waba_id e phone_number_id identificam o lojista
    id = Column(Integer, primary_key=True, index=True)
    waba_id = Column(String, unique=True, index=True, nullable=False)
    phone_number_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True) # Ex: Loja Teste
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MessageLog(Base):
    __tablename__ = "message_logs"

    # Log de mensagens para auditoria
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String, unique=True, index=True, nullable=False)
    waba_id = Column(String, index=True, nullable=False)
    user_phone = Column(String, index=True, nullable=False)
    direction = Column(String, nullable=False) # 'inbound' ou 'outbound'
    content = Column(String, nullable=True)    # Texto ou tipo
    status = Column(String, nullable=False, default="received") # received, sent, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
