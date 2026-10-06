from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Equipamento(Base):
    __tablename__ = "equipamentos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    tag = Column(String, unique=True, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    status = Column(String, default="Operacional") # Operacional, Alerta, Parada Não Planejada
    
    # Relacionamento com as Ordens de Serviço
    ordens = relationship("OrdemServico", back_populates="equipamento")


class OrdemServico(Base):
    __tablename__ = "ordens_servico"

    id = Column(Integer, primary_key=True, index=True)
    equipamento_id = Column(Integer, ForeignKey("equipamentos.id"))
    diagnostico_ia = Column(String) # Ex: "Eixo travado", "Motor Queimado"
    
    # Métricas de Tempo e Despacho
    sla_chegada_minutos = Column(Integer) # Calculado pela API Externa (OSRM)
    mttr_estimado_horas = Column(Float) # Tempo médio de reparo estimado
    tempo_real_operador = Column(Float, default=0.0) # Atualizado em tempo real pelo Front-end
    
    # Métricas Financeiras
    custo_total = Column(Float, default=0.0) # Materiais + Hora/Homem
    status_os = Column(String, default="Aberta") # Aberta, Em Andamento, Concluída
    data_abertura = Column(DateTime, default=datetime.utcnow)

    equipamento = relationship("Equipamento", back_populates="ordens")