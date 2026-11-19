from unittest.mock import MagicMock, patch
import pytest
from database import get_db


def test_status_check(unit_client):
    response = unit_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "API ativa e operacional"}


def test_obter_kpis_globais_retorno(unit_client, mock_db):
    mock_row = {
        "total_ingressantes": 1000,
        "total_ingressantes_mulheres": 200,
        "pct_ingressantes_mulheres": 20.0,
    }
    mock_db.execute.return_value.mappings.return_value.first.return_value = mock_row

    response = unit_client.get("/api/v1/kpis/geral")

    assert response.status_code == 200
    assert response.json() == mock_row
    mock_db.execute.assert_called_once()


def test_obter_evolucao_temporal_retorno(unit_client, mock_db):
    mock_rows = [
        {"year": 2023, "total_matriculas": 500, "pct_matriculas_mulheres": 18.5},
        {"year": 2024, "total_matriculas": 600, "pct_matriculas_mulheres": 19.2},
    ]
    mock_db.execute.return_value.mappings.return_value.all.return_value = mock_rows

    response = unit_client.get("/api/v1/metricas/evolucao-temporal")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["year"] == 2023


def test_obter_ranking_cursos_parametros_padrao_e_customizados(unit_client, mock_db):
    mock_db.execute.return_value.mappings.return_value.all.return_value = []

    # 1. Chamada sem parâmetros deve usar min_matriculas=5000 e limit=10
    resp_default = unit_client.get("/api/v1/metricas/cursos")
    assert resp_default.status_code == 200
    _, params_default = mock_db.execute.call_args[0]
    assert params_default == {"min_matriculas": 5000, "limit": 10}

    # 2. Chamada com parâmetros explícitos
    resp_custom = unit_client.get("/api/v1/metricas/cursos?min_matriculas=1200&limit=5")
    assert resp_custom.status_code == 200
    _, params_custom = mock_db.execute.call_args[0]
    assert params_custom == {"min_matriculas": 1200, "limit": 5}


def test_obter_ranking_cursos_parametro_invalido_retorna_422(unit_client):
    response = unit_client.get("/api/v1/metricas/cursos?min_matriculas=texto_invalido")
    assert response.status_code == 422


def test_filtrar_dados_metricas_normalizacao_caixa_alta(unit_client, mock_db):
    mock_db.execute.return_value.mappings.return_value.all.return_value = []

    response = unit_client.get("/api/v1/metricas/filtrar?ano=2024&uf=pi&curso=ciencia&limit=20")

    assert response.status_code == 200
    _, params = mock_db.execute.call_args[0]
    assert params == {
        "ano": 2024,
        "uf": "PI",
        "curso": "CIENCIA",
        "limit": 20,
    }


def test_filtrar_dados_metricas_sem_filtros(unit_client, mock_db):
    mock_db.execute.return_value.mappings.return_value.all.return_value = []

    response = unit_client.get("/api/v1/metricas/filtrar")

    assert response.status_code == 200
    _, params = mock_db.execute.call_args[0]
    assert params == {
        "ano": None,
        "uf": None,
        "curso": None,
        "limit": 50,
    }


def test_get_db_fecha_sessao_mesmo_com_excecao():
    fake_session = MagicMock()
    with patch("database.SessionLocal", return_value=fake_session):
        gen = get_db()
        db = next(gen)
        assert db is fake_session

        with pytest.raises(RuntimeError):
            gen.throw(RuntimeError("Erro simulado na rota"))

        fake_session.close.assert_called_once()


def test_obter_kpis_globais_tabela_vazia_retorna_objeto_vazio(unit_client, mock_db):
    mock_db.execute.return_value.mappings.return_value.first.return_value = None

    response = unit_client.get("/api/v1/kpis/geral")

    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.parametrize("query_string", [
    "limit=0",
    "limit=-5",
    "limit=501",
    "min_matriculas=-1",
])
def test_obter_ranking_cursos_limites_invalidos_retorna_422(unit_client, query_string):
    response = unit_client.get(f"/api/v1/metricas/cursos?{query_string}")
    assert response.status_code == 422


@pytest.mark.parametrize("query_string", [
    "ano=2008",
    "ano=2025",
    "uf=A",
    "uf=ABC",
    "limit=0",
])
def test_filtrar_dados_metricas_filtros_fora_do_dominio_retorna_422(unit_client, query_string):
    response = unit_client.get(f"/api/v1/metricas/filtrar?{query_string}")
    assert response.status_code == 422