from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import get_db


# ---------------------------------------------------------
# Fixtures para Testes Unitários (Sessão Mockada)
# ---------------------------------------------------------
@pytest.fixture
def mock_db():
    """Retorna uma sessão SQLAlchemy simulada para testes unitários."""
    session = MagicMock()
    return session


@pytest.fixture
def unit_client(mock_db):
    """Cliente FastAPI com injeção de dependência mockada."""
    def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


# ---------------------------------------------------------
# Fixtures para Testes de Integração (Star Schema em Memória)
# ---------------------------------------------------------
@pytest.fixture
def integration_db():
    """Cria e popula o Star Schema em memória para validar as queries SQL reais."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Registra CONCAT no SQLite para compatibilidade com a sintaxe MySQL de queries.py
    @event.listens_for(engine, "connect")
    def register_mysql_functions(dbapi_connection, connection_record):
        dbapi_connection.create_function(
            "CONCAT", -1, lambda *args: "".join(str(a) for a in args if a is not None)
        )

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()

    # DDL espelhando as tabelas fact_metrics, dim_location e dim_program
    db.execute(text("""
        CREATE TABLE dim_location (
            id_location INTEGER PRIMARY KEY,
            state_code TEXT
        );
    """))
    db.execute(text("""
        CREATE TABLE dim_program (
            id_program INTEGER PRIMARY KEY,
            program_name TEXT
        );
    """))
    db.execute(text("""
        CREATE TABLE fact_metrics (
            id_fact INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER,
            id_location INTEGER,
            id_program INTEGER,
            entrants_count REAL,
            female_entrants_count REAL,
            enrolled_count REAL,
            female_enrolled_count REAL,
            graduates_count REAL,
            female_graduates_count REAL
        );
    """))

    # Carga de dados controlados (Seed)
    db.execute(text("""
        INSERT INTO dim_location (id_location, state_code) VALUES
        (1, 'PI'),
        (2, 'SP'),
        (3, 'Not reported');
    """))
    db.execute(text("""
        INSERT INTO dim_program (id_program, program_name) VALUES
        (1, 'CIENCIA DA COMPUTACAO'),
        (2, 'ANALISE E DESENVOLVIMENTO DE SISTEMAS'),
        (3, 'ENGENHARIA DE SOFTWARE');
    """))
    db.execute(text("""
        INSERT INTO fact_metrics (
            year, id_location, id_program,
            entrants_count, female_entrants_count,
            enrolled_count, female_enrolled_count,
            graduates_count, female_graduates_count
        ) VALUES
        -- PI | Ciência da Computação | 2023 (25% mulheres matriculadas)
        (2023, 1, 1, 200, 50, 1000, 250, 100, 30),
        -- SP | ADS | 2024 (20% mulheres matriculadas, volume alto)
        (2024, 2, 2, 1000, 200, 6000, 1200, 800, 160),
        -- SP | Engenharia de Software | 2024 (50% mulheres, mas volume abaixo de 5000)
        (2024, 2, 3, 100, 50, 400, 200, 50, 25),
        -- Registro 'Not reported' (deve ser ignorado no ranking de estados)
        (2024, 3, 1, 50, 10, 200, 40, 20, 4);
    """))
    db.commit()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def integration_client(integration_db):
    """Cliente FastAPI conectado ao banco relacional de teste."""
    def override_get_db():
        yield integration_db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()