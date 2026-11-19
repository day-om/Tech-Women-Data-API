import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Conclusões Analíticas | Tech Women Data",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Mesma identidade visual do dashboard principal
st.markdown(
    """
    <style>
    .hero-banner {
        background: linear-gradient(135deg, #581C87 0%, #9333EA 55%, #DB2777 100%);
        padding: 1.8rem 2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px -5px rgba(147, 51, 234, 0.25);
    }
    .hero-banner h1 {
        margin: 0;
        font-size: 1.95rem;
        font-weight: 700;
        color: #FFFFFF;
    }
    .hero-banner p {
        margin: 0.5rem 0 0 0;
        font-size: 1rem;
        color: #F3E8FF;
    }
    .insight-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 5px solid #9333EA;
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
        height: 100%;
    }
    .insight-card.pink { border-left-color: #DB2777; }
    .insight-card.indigo { border-left-color: #4F46E5; }
    .insight-tag {
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #9333EA;
        margin-bottom: 0.35rem;
    }
    .insight-card.pink .insight-tag { color: #DB2777; }
    .insight-card.indigo .insight-tag { color: #4F46E5; }
    .insight-metric {
        font-size: 1.75rem;
        font-weight: 800;
        color: #1E293B;
        line-height: 1.15;
    }
    .insight-text {
        font-size: 0.9rem;
        color: #475569;
        margin-top: 0.5rem;
        line-height: 1.45;
    }
    .notebook-box {
        background-color: #FAF5FF;
        border: 1px solid #E9D5FF;
        border-radius: 12px;
        padding: 1rem 1.3rem;
        margin-bottom: 1.5rem;
        color: #3B0764;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    [data-testid="stSidebarNav"],
    [data-testid="stSidebarNavItems"],
    [data-testid="stSidebarNavSeparator"] {
        display: none !important;
    }
    [data-testid="stPlotlyChart"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 0.35rem;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Barra lateral
with st.sidebar:
    st.markdown("### 👩‍💻 Tech Women Data")
    st.caption("Síntese Executiva & Achados da Pesquisa (INEP 2009–2024)")
    st.divider()

    st.markdown("**Navegação:**")
    st.page_link(
        "dashboard.py",
        label="Observatório Interativo",
        icon="👩‍💻",
        use_container_width=True,
    )
    st.page_link(
        "pages/1_📊_Conclusoes_Analiticas.py",
        label="Conclusões Analíticas (2009–2024)",
        icon="📊",
        use_container_width=True,
    )
    st.divider()

    st.markdown("**Metodologia & Pipeline:**")
    st.caption(
        "Extração SQL via BigQuery (Base dos Dados), limpeza e análise exploratória em Python "
        "(Pandas, Matplotlib e Seaborn)."
    )
    st.markdown("**Notebook de Referência:**")
    st.code("notebooks/Tech_Women_Data_API.ipynb", language="text")


# Cabeçalho principal
st.markdown(
    '<div class="hero-banner">'
    "<h1>📊 Principais Conclusões Analíticas (2009–2024)</h1>"
    "<p>Síntese dos achados sobre ingresso, permanência, distribuição regional e perfil dos cursos de TI no Brasil.</p>"
    "</div>",
    unsafe_allow_html=True,
)

# Destaque do Notebook
st.markdown(
    """
    <div class="notebook-box">
        📓 <b>Código completo e gráficos exploratórios:</b> A extração completa de SQL do BigQuery, o pipeline de limpeza de dados
        e as visualizações estatísticas em Matplotlib/Seaborn estão documentados em
        <code>notebooks/Tech_Women_Data_API.ipynb</code>.
    </div>
    """,
    unsafe_allow_html=True,
)

# 1. Resumo da Trajetória Acadêmica Feminina (Cards + Tabela)
st.subheader("🏁 Resumo da Trajetória Acadêmica Feminina (2009–2024)")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(
        """
        <div class="insight-card">
            <div class="insight-tag">1. Entrada (Ingressantes)</div>
            <div class="insight-metric">21,30% em 2024</div>
            <div class="insight-text">
                <b>104.176 novas alunas/ano</b> no pico histórico (média cumulativa de <b>17,59%</b>),
                após superar o vale de <b>13,43%</b> registrado em 2017.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        """
        <div class="insight-card pink">
            <div class="insight-tag">2. Persistência (Matrículas Ativas)</div>
            <div class="insight-metric">19,24% em 2024</div>
            <div class="insight-text">
                <b>153.931 estudantes ativas</b> em 2024 (triplicando o volume de 2009). No acumulado,
                são <b>1,03 milhão</b> de matrículas femininas (<b>16,12%</b> de 6,4 mi).
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        """
        <div class="insight-card indigo">
            <div class="insight-tag">3. Conclusão (Graduadas)</div>
            <div class="insight-metric">19,16% em 2024</div>
            <div class="insight-text">
                <b>19.253 novas profissionais</b> formadas em 2024. No total de 15 anos, são
                <b>132.057 mulheres</b> graduadas (<b>16,21%</b> de 814.758 formados).
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

df_resumo = pd.DataFrame(
    [
        {
            "Etapa da Jornada": "Entrada (Ingressantes)",
            "Média Histórica Cumulativa": "17,59%",
            "Menor Patamar (Vale)": "13,43% (2017)",
            "Situação Atual (2024 — Recorde Histórico)": "21,30% (104.176 novas alunas/ano)",
        },
        {
            "Etapa da Jornada": "Persistência (Matrículas Ativas)",
            "Média Histórica Cumulativa": "16,12%",
            "Menor Patamar (Vale)": "13,16% (2018)",
            "Situação Atual (2024 — Recorde Histórico)": "19,24% (153.931 estudantes ativas)",
        },
        {
            "Etapa da Jornada": "Conclusão (Graduadas / Mercado)",
            "Média Histórica Cumulativa": "16,21%",
            "Menor Patamar (Vale)": "~13,20% (2018–2019)",
            "Situação Atual (2024 — Recorde Histórico)": "19,16% (19.253 novas graduadas/ano)",
        },
    ]
)
st.dataframe(df_resumo, use_container_width=True, hide_index=True)

st.info(
    "**O Fenômeno da Curva em 'U' e a Paridade Acadêmica:** Os três indicadores exibem um declínio sistemático "
    "a partir de 2009 até o ponto crítico entre 2017 e 2019 (~13%), seguido de recuperação acelerada a partir de 2020 até "
    "os recordes de 2024. Além disso, o alinhamento entre a taxa acumulada de matrículas (**16,12%**) e de conclusão "
    "(**16,21%**) demonstra que as mulheres que ingressam e permanecem nos cursos de TI concluem a graduação em proporção "
    "equivalente ou superior à média geral."
)

st.divider()

# 2. Detalhamento por Dimensão (Abas Temáticas)
tab_trajetoria, tab_uf, tab_cursos = st.tabs(
    [
        "📈 Dinâmica Temporal (2009–2024)",
        "🗺️ Distribuição Geográfica (UF)",
        "🎓 Participação por Perfil de Curso",
    ]
)

with tab_trajetoria:
    col_t1, col_t2 = st.columns([1.3, 1], gap="large")

    with col_t1:
        st.markdown("#### Marcos da Evolução de Ingressantes Mulheres")
        marcos_anos = ["2009 (Início)", "2017 (Vale)", "2018 (Virada)", "2020", "2021", "2024 (Recorde)"]
        marcos_pct = [17.08, 13.43, 13.71, 16.58, 18.95, 21.30]
        cores_barras = ["#9333EA", "#94A3B8", "#A855F7", "#C026D3", "#DB2777", "#BE185D"]

        fig_marcos = go.Figure(
            data=[
                go.Bar(
                    x=marcos_anos,
                    y=marcos_pct,
                    text=[f"{v:.2f}%" for v in marcos_pct],
                    textposition="outside",
                    marker_color=cores_barras,
                )
            ]
        )
        fig_marcos.update_layout(
            yaxis=dict(title="Ingressantes Mulheres (%)", range=[0, 25]),
            xaxis=dict(title=""),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            height=360,
            margin=dict(l=20, r=20, t=30, b=20),
        )
        st.plotly_chart(fig_marcos, use_container_width=True)

    with col_t2:
        st.markdown("#### Síntese dos Três Estágios")
        st.markdown(
            """
            * **Ingressantes:** Partiu de **17,08%** (2009) até o mínimo de **13,43%** (2017). A virada começou em 2018
              (**13,71%**), avançou em 2020 (**16,58%**) e 2021 (**18,95%**), atingindo **21,30%** em 2024.
            * **Matrículas Ativas:** Recuou de **17,23%** (2009) para **13,16%** (2018), recuperando-se até **19,24%**
              em 2024 — **triplicando** o contingente absoluto de mulheres em sala de aula frente a 2009.
            * **Concluintes:** Em 15 anos, o Brasil formou **814.758** profissionais de TI, sendo **132.057 mulheres**.
              Apenas em 2024, **19.253** mulheres concluíram a graduação (**19,16%**).
            """
        )

with tab_uf:
    col_u1, col_u2 = st.columns(2, gap="large")

    with col_u1:
        st.markdown("#### Destaque em Volume vs. Proporção")
        st.success(
            "**🏆 Líderes em Representação Proporcional:** Excluindo registros não declarados, o **Amazonas (AM)** lidera o "
            "país com **18,4%** de mulheres matriculadas e **18,8%** de graduadas, seguido pelo **Pará (PA)** e **Alagoas (AL)**."
        )
        st.info(
            "**🏢 Polo Dominante em Escala:** **São Paulo (SP)** concentra mais de **2,1 milhões** de matrículas e "
            "**320.908 graduados** acumulados, sustentando uma taxa feminina estável entre **17,4% e 17,6%**."
        )

    with col_u2:
        st.markdown("#### Desafios de Inclusão entre Grandes Polos")
        df_desafios = pd.DataFrame(
            {
                "Estado": ["Amazonas (Líder)", "São Paulo (Polo)", "Paraná (PR)", "Rio Grande do Sul (RS)", "Bahia (BA)"],
                "Graduadas (%)": [18.80, 17.50, 13.89, 13.76, 13.58],
            }
        ).sort_values("Graduadas (%)", ascending=True)

        fig_uf_comp = go.Figure(
            data=[
                go.Bar(
                    y=df_desafios["Estado"],
                    x=df_desafios["Graduadas (%)"],
                    orientation="h",
                    text=[f"{v:.2f}%" for v in df_desafios["Graduadas (%)"]],
                    textposition="outside",
                    marker_color=["#64748B", "#64748B", "#64748B", "#9333EA", "#DB2777"],
                )
            ]
        )
        fig_uf_comp.update_layout(
            xaxis=dict(title="Mulheres Graduadas (%)", range=[0, 23]),
            yaxis=dict(title=""),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            height=300,
            margin=dict(l=10, r=20, t=20, b=20),
        )
        st.plotly_chart(fig_uf_comp, use_container_width=True)

with tab_cursos:
    col_c1, col_c2 = st.columns([1.15, 1], gap="large")

    with col_c1:
        st.markdown("#### Cursos que Impulsionam vs. Cursos com Maior Barreira")
        cursos_comparativo = pd.DataFrame(
            [
                {"Curso / Área": "Informática Empresarial", "Participação (%)": 26.0, "Perfil": "Interdisciplinar / Negócios"},
                {"Curso / Área": "Ciência de Dados / Big Data", "Participação (%)": 23.5, "Perfil": "Interdisciplinar / Dados"},
                {"Curso / Área": "Sistemas de Internet / Gestão de TI", "Participação (%)": 19.5, "Perfil": "Interdisciplinar / Gestão"},
                {"Curso / Área": "Análise e Desenv. de Sistemas (ADS)", "Participação (%)": 16.83, "Perfil": "Maior Volume Nacional"},
                {"Curso / Área": "Ciência da Computação", "Participação (%)": 13.33, "Perfil": "Bacharelado Tradicional"},
                {"Curso / Área": "Redes de Computadores", "Participação (%)": 8.00, "Perfil": "Infraestrutura / Tradicional"},
            ]
        ).sort_values("Participação (%)", ascending=True)

        cores_cursos = [
            "#94A3B8" if v < 15 else ("#9333EA" if v < 18 else "#DB2777")
            for v in cursos_comparativo["Participação (%)"]
        ]

        fig_cursos_resumo = go.Figure(
            data=[
                go.Bar(
                    y=cursos_comparativo["Curso / Área"],
                    x=cursos_comparativo["Participação (%)"],
                    orientation="h",
                    text=[f"{v:.1f}%" for v in cursos_comparativo["Participação (%)"]],
                    textposition="outside",
                    marker_color=cores_cursos,
                )
            ]
        )
        fig_cursos_resumo.update_layout(
            xaxis=dict(title="Participação Feminina (%)", range=[0, 31]),
            yaxis=dict(title=""),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            height=360,
            margin=dict(l=10, r=20, t=20, b=20),
        )
        st.plotly_chart(fig_cursos_resumo, use_container_width=True)

    with col_c2:
        st.markdown("#### Principais Padrões Identificados")
        st.markdown(
            """
            * **Fatores de Atração (Negócios, Gestão e Dados):** Cursos que conectam tecnologia à tomada de decisão e
              negócios concentram as maiores taxas femininas — **Informática Empresarial** supera **26%**, **Ciência de Dados /
              Big Data** alcança **22% a 25%**, e **Sistemas de Internet / Gestão de TI** fica entre **19% e 20%**.
            * **Escala do ADS:** **Análise e Desenvolvimento de Sistemas** é o maior curso em volume do Brasil
              (**282.311 graduados acumulados**), registrando **14,5%** de matrículas e **16,83%** de concluídas mulheres.
            * **Barreira nos Cursos Tradicionais:** Bacharelados clássicos como **Ciência da Computação** (**13,33%** de
              graduadas) e formações focadas em infraestrutura como **Redes de Computadores** (**8,00%**) apresentam os
              maiores desafios de atração e retenção.
            """
        )