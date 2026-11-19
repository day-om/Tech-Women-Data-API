"""
queries.py
Consultas SQL analíticas para a Tech Women Data API
Modelagem: Star Schema (fact_metrics, dim_program, dim_location)
"""

# 1. Visão Geral (Métricas Globais Acumuladas)
QUERY_KPIS_GLOBAIS = """
    SELECT 
        SUM(entrants_count) AS total_ingressantes,
        SUM(female_entrants_count) AS total_ingressantes_mulheres,
        ROUND((SUM(female_entrants_count) / NULLIF(SUM(entrants_count), 0)) * 100, 2) AS pct_ingressantes_mulheres,
        
        SUM(enrolled_count) AS total_matriculados,
        SUM(female_enrolled_count) AS total_matriculados_mulheres,
        ROUND((SUM(female_enrolled_count) / NULLIF(SUM(enrolled_count), 0)) * 100, 2) AS pct_matriculados_mulheres,
        
        SUM(graduates_count) AS total_concluintes,
        SUM(female_graduates_count) AS total_concluintes_mulheres,
        ROUND((SUM(female_graduates_count) / NULLIF(SUM(graduates_count), 0)) * 100, 2) AS pct_concluintes_mulheres
    FROM fact_metrics;
"""

# 2. Evolução Temporal (Para Gráficos de Linha - Série Histórica 2009-2024)
QUERY_EVOLUCAO_TEMPORAL = """
    SELECT 
        year,
        SUM(entrants_count) AS total_ingressantes,
        SUM(female_entrants_count) AS ingressantes_mulheres,
        ROUND((SUM(female_entrants_count) / NULLIF(SUM(entrants_count), 0)) * 100, 2) AS pct_ingressantes_mulheres,
        
        SUM(enrolled_count) AS total_matriculas,
        SUM(female_enrolled_count) AS matriculas_mulheres,
        ROUND((SUM(female_enrolled_count) / NULLIF(SUM(enrolled_count), 0)) * 100, 2) AS pct_matriculas_mulheres,
        
        SUM(graduates_count) AS total_concluintes,
        SUM(female_graduates_count) AS concluintes_mulheres,
        ROUND((SUM(female_graduates_count) / NULLIF(SUM(graduates_count), 0)) * 100, 2) AS pct_concluintes_mulheres
    FROM fact_metrics
    GROUP BY year
    ORDER BY year ASC;
"""

# 3. Análise Geográfica por Estado (JOIN com dim_location)
QUERY_RANKING_ESTADOS = """
    SELECT 
        l.state_code AS state_uf,
        SUM(f.enrolled_count) AS total_matriculas,
        SUM(f.female_enrolled_count) AS matriculas_mulheres,
        ROUND((SUM(f.female_enrolled_count) / NULLIF(SUM(f.enrolled_count), 0)) * 100, 2) AS pct_mulheres_matriculas,
        SUM(f.graduates_count) AS total_concluintes,
        SUM(f.female_graduates_count) AS concluintes_mulheres,
        ROUND((SUM(f.female_graduates_count) / NULLIF(SUM(f.graduates_count), 0)) * 100, 2) AS pct_mulheres_concluintes
    FROM fact_metrics f
    INNER JOIN dim_location l ON f.id_location = l.id_location
    WHERE l.state_code IS NOT NULL AND l.state_code != 'Not reported'
    GROUP BY l.state_code
    ORDER BY total_matriculas DESC;
"""

# 4. Análise por Cursos (JOIN com dim_program)
QUERY_RANKING_CURSOS = """
    SELECT 
        p.program_name AS course_name,
        SUM(f.enrolled_count) AS total_matriculas,
        SUM(f.female_enrolled_count) AS matriculas_mulheres,
        ROUND((SUM(f.female_enrolled_count) / NULLIF(SUM(f.enrolled_count), 0)) * 100, 2) AS pct_mulheres_matriculas,
        SUM(f.graduates_count) AS total_concluintes,
        SUM(f.female_graduates_count) AS concluintes_mulheres,
        ROUND((SUM(f.female_graduates_count) / NULLIF(SUM(f.graduates_count), 0)) * 100, 2) AS pct_mulheres_concluintes
    FROM fact_metrics f
    INNER JOIN dim_program p ON f.id_program = p.id_program
    GROUP BY p.program_name
    HAVING total_matriculas >= :min_matriculas
    ORDER BY pct_mulheres_matriculas DESC
    LIMIT :limit;
"""

# 5. Consulta flexível com múltiplos filtros opcionais
QUERY_DADOS_FILTRADOS = """
    SELECT 
        f.year,
        l.state_code AS state_uf,
        p.program_name AS course_name,
        SUM(f.entrants_count) AS total_ingressantes,
        SUM(f.female_entrants_count) AS ingressantes_mulheres,
        SUM(f.enrolled_count) AS total_matriculas,
        SUM(f.female_enrolled_count) AS matriculas_mulheres,
        SUM(f.graduates_count) AS total_concluintes,
        SUM(f.female_graduates_count) AS concluintes_mulheres
    FROM fact_metrics f
    INNER JOIN dim_location l ON f.id_location = l.id_location
    INNER JOIN dim_program p ON f.id_program = p.id_program
    WHERE (:ano IS NULL OR f.year = :ano)
      AND (:uf IS NULL OR l.state_code = :uf)
      AND (:curso IS NULL OR p.program_name LIKE CONCAT('%', :curso, '%'))
    GROUP BY f.year, l.state_code, p.program_name
    ORDER BY f.year DESC, total_matriculas DESC
    LIMIT :limit;
"""