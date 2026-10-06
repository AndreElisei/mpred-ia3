from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# --- Schemas para Equipamentos ---
class EquipamentoBase(BaseModel):
    nome: str
    tag: str
    latitude: float
    longitude: float

class EquipamentoCreate(EquipamentoBase):
    pass

class EquipamentoResponse(EquipamentoBase):
    id: int
    status: str

    class Config:
        from_attributes = True

# --- Schemas para Ordem de Serviço ---
class OrdemServicoUpdate(BaseModel):
    tempo_real_operador: Optional[float] = None
    custo_total: Optional[float] = None
    status_os: Optional[str] = None

class OrdemServicoResponse(BaseModel):
    id: int
    equipamento_id: int
    diagnostico_ia: str
    sla_chegada_minutos: int
    mttr_estimado_horas: float
    tempo_real_operador: float
    custo_total: float
    status_os: str
    data_abertura: datetime

    class Config:
        from_attributes = True