def test_integracao_kpis_globais(integration_client):
    response = integration_client.get("/api/v1/kpis/geral")
    assert response.status_code == 200

    dados = response.json()
    # Soma de todos os registros inseridos no seed:
    # Ingressantes: 200 + 1000 + 100 + 50 = 1350 | Mulheres: 50 + 200 + 50 + 10 = 310
    assert dados["total_ingressantes"] == 1350
    assert dados["total_ingressantes_mulheres"] == 310
    assert dados["pct_ingressantes_mulheres"] == round((310 / 1350) * 100, 2)

    # Matriculados: 1000 + 6000 + 400 + 200 = 7600 | Mulheres: 250 + 1200 + 200 + 40 = 1690
    assert dados["total_matriculados"] == 7600
    assert dados["total_matriculados_mulheres"] == 1690
    assert dados["pct_matriculados_mulheres"] == round((1690 / 7600) * 100, 2)


def test_integracao_evolucao_temporal_ordenacao_asc(integration_client):
    response = integration_client.get("/api/v1/metricas/evolucao-temporal")
    assert response.status_code == 200

    serie = response.json()
    assert len(serie) == 2
    assert [item["year"] for item in serie] == [2023, 2024]
    assert serie[0]["total_matriculas"] == 1000
    assert serie[0]["pct_matriculas_mulheres"] == 25.0


def test_integracao_ranking_estados_exclui_not_reported_e_ordena_desc(integration_client):
    response = integration_client.get("/api/v1/metricas/estados")
    assert response.status_code == 200

    estados = response.json()
    ufs = [e["state_uf"] for e in estados]

    # 'Not reported' deve ser filtrado pela cláusula WHERE
    assert "Not reported" not in ufs
    # SP (6400 matrículas) deve vir antes de PI (1000 matrículas)
    assert ufs == ["SP", "PI"]
    assert estados[0]["total_matriculas"] == 6400
    assert estados[1]["total_matriculas"] == 1000


def test_integracao_ranking_cursos_aplica_having_min_matriculas(integration_client):
    # Com min_matriculas padrão (5000), apenas ADS (6000) atende ao critério HAVING
    resp_default = integration_client.get("/api/v1/metricas/cursos")
    assert resp_default.status_code == 200
    cursos_default = resp_default.json()
    assert len(cursos_default) == 1
    assert cursos_default[0]["course_name"] == "ANALISE E DESENVOLVIMENTO DE SISTEMAS"

    # Reduzindo min_matriculas para 300, todos os 3 cursos entram ordenados por pct_mulheres_matriculas DESC
    resp_todos = integration_client.get("/api/v1/metricas/cursos?min_matriculas=300")
    cursos_todos = resp_todos.json()
    assert [c["course_name"] for c in cursos_todos] == [
        "ENGENHARIA DE SOFTWARE",               # 50.0%
        "CIENCIA DA COMPUTACAO",                # 25.0%
        "ANALISE E DESENVOLVIMENTO DE SISTEMAS" # 20.0%
    ]


def test_integracao_filtrar_dados_combinacao_dinamica(integration_client):
    # Filtro por UF e trecho parcial do curso em minúsculo
    response = integration_client.get("/api/v1/metricas/filtrar?uf=pi&curso=ciencia")
    assert response.status_code == 200

    resultados = response.json()
    assert len(resultados) == 1
    assert resultados[0]["year"] == 2023
    assert resultados[0]["state_uf"] == "PI"
    assert resultados[0]["course_name"] == "CIENCIA DA COMPUTACAO"


def test_integracao_filtrar_dados_sem_correspondencia(integration_client):
    response = integration_client.get("/api/v1/metricas/filtrar?ano=2010&uf=AM")
    assert response.status_code == 200
    assert response.json() == []