from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from typing import List
from ..database import get_db
from ..models import HealthRecord, User
from ..schemas import HealthRecordCreate, HealthRecordResponse
from ..routes.auth import get_current_user
from ..services.blockchain import BlockchainService
from datetime import datetime
from ..logging_config import logger

router = APIRouter(prefix="/records", tags=["health records"])

@router.post("/", response_model=HealthRecordResponse)
async def create_record(
    record: HealthRecordCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "doctor":
        logger.warning(f"Tentativa de acesso negado: Usuário {current_user.username} tentou criar registro sem ser médico.")
        raise HTTPException(status_code=403, detail="Apenas médicos podem criar registros")
    
    logger.info(f"Médico {current_user.username} iniciando criação de prontuário para paciente {record.patient_id}")
    
    # Buscar o último registro para obter o previous_hash
    result = await db.execute(
        select(HealthRecord).order_by(desc(HealthRecord.timestamp)).limit(1)
    )
    last_record = result.scalars().first()
    previous_hash = last_record.hash if last_record else "0" * 64
    
    # Preparar dados para o hash
    record_data = record.dict()
    record_data["doctor_id"] = current_user.id
    record_data["timestamp"] = datetime.utcnow()
    
    # Calcular o hash do novo bloco
    new_hash = BlockchainService.calculate_hash(record_data, previous_hash)
    
    db_record = HealthRecord(
        **record.dict(),
        doctor_id=current_user.id,
        timestamp=record_data["timestamp"],
        previous_hash=previous_hash,
        hash=new_hash
    )
    
    db.add(db_record)
    await db.commit()
    await db.refresh(db_record)
    return db_record

@router.get("/", response_model=List[HealthRecordResponse])
async def get_records(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Pacientes só veem seus próprios registros, médicos veem todos (para simplificar o TCC)
    if current_user.role == "patient":
        query = select(HealthRecord).where(HealthRecord.patient_id == current_user.id)
    else:
        query = select(HealthRecord)
        
    result = await db.execute(query.order_by(HealthRecord.timestamp))
    return result.scalars().all()

@router.get("/verify")
async def verify_integrity(db: AsyncSession = Depends(get_db)):
    """
    Rota de auditoria para verificar a integridade da 'Blockchain'.
    """
    result = await db.execute(select(HealthRecord).order_by(HealthRecord.timestamp))
    records = result.scalars().all()
    
    is_valid = BlockchainService.verify_chain(records)
    return {"is_valid": is_valid, "total_records": len(records)}
