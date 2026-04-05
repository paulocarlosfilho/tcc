from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# --- CONFORMIDADE LGPD ---
# Os modelos abaixo seguem os princípios de:
# 1. Integridade (Blockchain): Garantia de que o dado não foi alterado.
# 2. Finalidade: Armazenamento apenas de dados necessários para o histórico clínico.
# 3. Segurança: Controle de acesso via relacionamento com usuários autenticados.

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)  # 'doctor' or 'patient'
    
    # Relacionamento para auditoria: saber qual médico criou qual registro
    records = relationship("HealthRecord", back_populates="creator")

class HealthRecord(Base):
    __tablename__ = "health_records"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, index=True)
    diagnosis = Column(Text)
    treatment = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Elo da Corrente (Blockchain)
    previous_hash = Column(String, index=True)
    hash = Column(String, unique=True, index=True)
    
    # Auditoria LGPD: ID do profissional responsável
    doctor_id = Column(Integer, ForeignKey("users.id"))
    creator = relationship("User", back_populates="records")
