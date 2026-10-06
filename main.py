from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import requests
import random

import models, schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RCM 4.0 - API de Telemetria e Logística de Manutenção",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Coordenadas fictícias da Sede da RCM 4.0 (Usaremos Resende, RJ como exemplo base)
BASE_LAT = -22.469
BASE_LON = -44.449

# 1. ROTA POST: Criar um equipamento
@app.post("/ativos", response_model=schemas.EquipamentoResponse, tags=["Gestão de Ativos"])
def criar_ativo(ativo: schemas.EquipamentoCreate, db: Session = Depends(get_db)):
    db_ativo = models.Equipamento(**ativo.model_dump())
    db.add(db_ativo)
    db.commit()
    db.refresh(db_ativo)
    return db_ativo

# 2. ROTA GET: Listar todos os equipamentos
@app.get("/ativos", response_model=list[schemas.EquipamentoResponse], tags=["Gestão de Ativos"])
def listar_ativos(db: Session = Depends(get_db)):
    return db.query(models.Equipamento).all()

# 3. ROTA DELETE: Remover um equipamento
@app.delete("/ativos/{id}", tags=["Gestão de Ativos"])
def deletar_ativo(id: int, db: Session = Depends(get_db)):
    db_ativo = db.query(models.Equipamento).filter(models.Equipamento.id == id).first()
    if not db_ativo:
        raise HTTPException(status_code=404, detail="Ativo não encontrado")
    db.delete(db_ativo)
    db.commit()
    return {"mensagem": "Ativo removido com sucesso"}

# 4. ROTA GET (Telemetria Simulada): Lógica de Negócio para o Diretor
@app.get("/ativos/{id}/telemetria", tags=["Inteligência e Diagnóstico"])
def ler_telemetria(id: int, db: Session = Depends(get_db)):
    db_ativo = db.query(models.Equipamento).filter(models.Equipamento.id == id).first()
    if not db_ativo:
        raise HTTPException(status_code=404, detail="Ativo não encontrado")
    
    # Adicionamos apenas um pequeno "ruído" para os números parecerem sensores reais vivos
    ruido_vib = random.uniform(-0.5, 0.5)
    ruido_temp = random.uniform(-1.5, 1.5)

    # Baseamos o estado do equipamento no seu ID para ser sempre consistente
    if id % 3 == 1: # Equipamentos 1, 4, 7... (Simula Motor Queimado)
        vib = round(1.0 + ruido_vib, 2)
        temp = round(105.0 + ruido_temp, 2)
    elif id % 3 == 2: # Equipamentos 2, 5, 8... (Simula Eixo Travado)
        vib = round(12.0 + ruido_vib, 2)
        temp = round(85.0 + ruido_temp, 2)
    else: # Equipamentos 3, 6, 9... (Simula Estado Normal)
        vib = round(2.5 + ruido_vib, 2)
        temp = round(45.0 + ruido_temp, 2)
    
    # Motor de Diagnóstico Baseado em Regras (agora os diagnósticos não saltam)
    diagnostico = "Normal"
    mttr = 0.0
    
    if vib > 10 and temp > 80:
        diagnostico = "Crítico: Eixo Travado / Rolamento Danificado"
        mttr = 4.5
    elif temp > 100:
        diagnostico = "Falha Catastrófica: Motor Queimado"
        mttr = 2.3
    elif vib > 7:
        diagnostico = "Alerta: Desalinhamento ou Engrenagem Empenada"
        mttr = 1.5
        
    return {
        "equipamento_id": id,
        "vibracao_mms": vib,
        "temperatura_c": temp,
        "diagnostico_ia": diagnostico,
        "mttr_estimado_horas": mttr
    }

# 5. ROTA POST (Consumo API Externa): Despacho de Técnico e Cálculo de Rota
@app.post("/ativos/{id}/despacho", response_model=schemas.OrdemServicoResponse, tags=["Inteligência e Diagnóstico"])
def despachar_equipe(id: int, diagnostico: str, mttr: float, db: Session = Depends(get_db)):
    db_ativo = db.query(models.Equipamento).filter(models.Equipamento.id == id).first()
    if not db_ativo:
        raise HTTPException(status_code=404, detail="Ativo não encontrado")
    
    # Integração com API Externa (OSRM) para calcular tempo de condução
    url = f"http://router.project-osrm.org/route/v1/driving/{BASE_LON},{BASE_LAT};{db_ativo.longitude},{db_ativo.latitude}?overview=false"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        # O OSRM devolve a duração em segundos. Convertendo para minutos:
        sla_minutos = int(data["routes"][0]["duration"] / 60)
    except:
        sla_minutos = 60 # SLA padrão caso a API externa sofra timeout
            
    # Muda o status do equipamento para que o front-end mostre em vermelho
    db_ativo.status = "Parada Não Planejada"
    
    nova_os = models.OrdemServico(
        equipamento_id=id,
        diagnostico_ia=diagnostico,
        sla_chegada_minutos=sla_minutos,
        mttr_estimado_horas=mttr
    )
    db.add(nova_os)
    db.commit()
    db.refresh(nova_os)
    return nova_os

# 6. ROTA PATCH: Atualizar Tempo e Custo da OS
@app.patch("/ordens/{id}", response_model=schemas.OrdemServicoResponse, tags=["Gestão de OS (Financeiro/Operacional)"])
def atualizar_os(id: int, os_update: schemas.OrdemServicoUpdate, db: Session = Depends(get_db)):
    db_os = db.query(models.OrdemServico).filter(models.OrdemServico.id == id).first()
    if not db_os:
        raise HTTPException(status_code=404, detail="Ordem de Serviço não encontrada")
        
    if os_update.tempo_real_operador is not None:
        db_os.tempo_real_operador = os_update.tempo_real_operador
    if os_update.custo_total is not None:
        db_os.custo_total = os_update.custo_total
    if os_update.status_os is not None:
        db_os.status_os = os_update.status_os
        
    db.commit()
    db.refresh(db_os)
    return db_os