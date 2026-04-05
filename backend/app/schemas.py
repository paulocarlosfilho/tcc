from pydantic import BaseModel, EmailStr, Field, constr
from datetime import datetime
from typing import Optional, List

# Esquemas de Usuário
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$")
    email: EmailStr
    role: str = Field(..., pattern="^(doctor|patient|admin|Médico|Paciente|Administrador)$")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=72)

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True

# Esquemas de Token
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Esquemas de Registro de Saúde (Blockchain)
class HealthRecordBase(BaseModel):
    patient_id: int = Field(..., gt=0)
    diagnosis: str = Field(..., min_length=2, max_length=500)
    treatment: str = Field(..., min_length=2, max_length=1000)

class HealthRecordCreate(HealthRecordBase):
    pass

class HealthRecordResponse(HealthRecordBase):
    id: int
    doctor_id: int
    timestamp: datetime
    hash: str
    previous_hash: Optional[str]

    class Config:
        from_attributes = True
