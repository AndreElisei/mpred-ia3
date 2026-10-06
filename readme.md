# RCM 4.0 - API de Telemetria e Logística de Manutenção

Este repositório contém a API Back-end (MVP 3) do sistema RCM 4.0, desenvolvida como requisito para a pós-graduação em Desenvolvimento Full-Stack da PUC-Rio.

O sistema atua no domínio da Engenharia de Confiabilidade e Gestão de Ativos. A API permite gerir equipamentos industriais, simular telemetria IoT (Vibração e Temperatura) e aplicar regras de negócio para gerar diagnósticos automáticos de falhas. Adicionalmente, integra-se com serviços de geolocalização para calcular o Tempo de Resposta (SLA) no despacho de equipas técnicas ou guinchos.

## Arquitetura do Sistema

A aplicação foi desenvolvida seguindo uma arquitetura baseada em serviços, em que o Front-end (React) consome esta API Principal (Python/FastAPI), que por sua vez consome uma API Externa de roteamento (OSRM). A persistência de dados é garantida por uma base de dados SQLite.

## Integração Externa (API OSRM)

Para o cálculo de rotas e tempo estimado de chegada (SLA) das equipas de manutenção ao local do ativo avariado, o sistema consome a API pública **OSRM (Open Source Routing Machine)**.
- **Documentação:** http://project-osrm.org/docs/v5.24.0/api/
- **Licença / Custo:** Gratuita e Open-Source.
- **Autenticação:** Não requer chave de API (No Auth).
- **Rota Consumida:** `/route/v1/driving/{lon_origem},{lat_origem};{lon_destino},{lat_destino}`

## Tecnologias Utilizadas

- **Python 3.10+**
- **FastAPI** (Web Framework e documentação Swagger automática)
- **SQLAlchemy** (ORM)
- **SQLite** (Base de Dados)
- **Docker & Docker Compose**

## Instruções de Instalação e Execução

A forma mais recomendada de executar este projeto é através do Docker, uma vez que o `docker-compose.yml` orquestra tanto a API como o Front-end simultaneamente.

### Opção 1: Execução via Docker (Recomendado)

1. Certifique-se de que tem o **Docker** e o **Docker Compose** instalados na sua máquina.
2. Clone este repositório e navegue até à diretoria:
   git clone https://github.com/AndreElisei/rcm-api-backend.git
   cd rcm-api-backend
3. Certifique-se de que clonou também o repositório do Front-end para a mesma diretoria "mãe", garantindo que as pastas `rcm-api-backend` e `mpred-ia-front` estão lado a lado.
4. Execute o comando de orquestração:
   docker compose up --build
5. A API estará disponível em: `http://localhost:8000`
6. A documentação Swagger interativa estará acessível em: `http://localhost:8000/docs`

### Opção 2: Execução Local (Manual)

Caso prefira rodar a API localmente sem Docker:

1. Clone o repositório e aceda à pasta:
   git clone https://github.com/AndreElisei/rcm-api-backend.git
   cd rcm-api-backend
2. Crie e ative um ambiente virtual:
   python -m venv venv
   .\venv\Scripts\activate
3. Instale as dependências:
   pip install -r requirements.txt
4. Execute o servidor:
   python -m uvicorn main:app --reload