from typing import Optional
from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
import queries

app = FastAPI(
    title="Tech Women Data API",
    description="API REST para consulta de dados sobre a representatividade e trajetória feminina no ensino superior de TI no Brasil (2009-2024)",
    version="1.0.0"
)

# 1. Rota de teste/status
@app.get("/", tags=["Status"])
def status_check():
    return {"status": "API ativa e operacional"}

# 2. Endpoint: KPIs Globais
@app.get("/api/v1/kpis/geral", tags=["Métricas"])
def obter_kpis_globais(db: Session = Depends(get_db)):
    """Retorna os indicadores consolidados acumulados (2009-2024)."""
    resultado = db.execute(text(queries.QUERY_KPIS_GLOBAIS)).mappings().first()
    return dict(resultado) if resultado else {}

# 3. Endpoint: Evolução Temporal
@app.get("/api/v1/metricas/evolucao-temporal", tags=["Métricas"])
def obter_evolucao_temporal(db: Session = Depends(get_db)):
    """Retorna a série histórica anual (2009-2024) do funil acadêmico."""
    resultado = db.execute(text(queries.QUERY_EVOLUCAO_TEMPORAL)).mappings().all()
    return [dict(row) for row in resultado]

# 4. Endpoint: Ranking por Estados (UF)
@app.get("/api/v1/metricas/estados", tags=["Métricas"])
def obter_ranking_estados(db: Session = Depends(get_db)):
    """Retorna métricas de volume e proporção agrupadas por Estado (UF)."""
    resultado = db.execute(text(queries.QUERY_RANKING_ESTADOS)).mappings().all()
    return [dict(row) for row in resultado]

# 5. Endpoint: Ranking por Cursos
@app.get("/api/v1/metricas/cursos", tags=["Métricas"])
def obter_ranking_cursos(
    min_matriculas: int = Query(5000, ge=0, description="Volume mínimo de matrículas para filtrar o curso"),
    limit: int = Query(10, ge=1, le=500, description="Quantidade de cursos no ranking"),
    db: Session = Depends(get_db)
):
    """Retorna o ranking de cursos por percentual de participação feminina."""
    resultado = db.execute(
        text(queries.QUERY_RANKING_CURSOS),
        {"min_matriculas": min_matriculas, "limit": limit}
    ).mappings().all()
    return [dict(row) for row in resultado]

# 6. Endpoint: Filtro Dinâmico
@app.get("/api/v1/metricas/filtrar", tags=["Métricas"])
def filtrar_dados_metricas(
    ano: Optional[int] = Query(None, ge=2009, le=2024, description="Filtrar por ano específico (ex: 2024)"),
    uf: Optional[str] = Query(None, min_length=2, max_length=2, description="Filtrar por sigla do estado (ex: PI, SP, AM)"),
    curso: Optional[str] = Query(None, min_length=1, description="Filtrar por trecho do nome do curso (ex: CIENCIA, ADS)"),
    limit: int = Query(50, ge=1, le=500, description="Limite de registros retornados"),
    db: Session = Depends(get_db)
):
    """
    Retorna métricas filtradas dinamicamente por Ano, UF ou Nome do Curso.
    Todos os filtros são opcionais.
    """
    params = {
        "ano": ano,
        "uf": uf.upper() if uf else None,
        "curso": curso.upper() if curso else None,
        "limit": limit
    }
    
    resultado = db.execute(text(queries.QUERY_DADOS_FILTRADOS), params).mappings().all()
    return [dict(row) for row in resultado]