import os
import requests
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Tech Women Data | Observatório TI (2009–2024)",
    page_icon="👩‍💻",
    layout="wide",
    initial_sidebar_state="expanded",
)

try:
    API_BASE_URL = st.secrets["API_BASE_URL"].rstrip("/")
except Exception:
    API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")

# Estilização CSS personalizada
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
        font-size: 2rem;
        font-weight: 700;
        color: #FFFFFF;
    }
    .hero-banner p {
        margin: 0.5rem 0 0 0;
        font-size: 1rem;
        color: #F3E8FF;
    }
    .kpi-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 5px solid #9333EA;
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
    }
    .kpi-card.pink { border-left-color: #DB2777; }
    .kpi-card.indigo { border-left-color: #4F46E5; }
    .kpi-title {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: #64748B;
        margin-bottom: 0.3rem;
    }
    .kpi-value {
        font-size: 2.1rem;
        font-weight: 800;
        color: #1E293B;
        line-height: 1.1;
    }
    .kpi-sub {
        font-size: 0.88rem;
        color: #475569;
        margin-top: 0.45rem;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    [data-testid="stSidebarNav"],
    [data-testid="stSidebarNavItems"],
    [data-testid="stSidebarNavSeparator"] {
        display: none !important;
    }
    .block-container {
        padding-top: 1.6rem;
        padding-bottom: 2rem;
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


# Funções auxiliares
def formatar_milhar(valor: int | float) -> str:
    return f"{int(valor):,}".replace(",", ".")


def calcular_total(mulheres: int, pct: float, total_direto: int | None = None) -> int:
    if total_direto is not None and total_direto > 0:
        return int(total_direto)
    if pct and pct > 0:
        return int(round(mulheres / (pct / 100)))
    return int(mulheres)


@st.cache_data(ttl=300)
def fetch_api(endpoint: str, params: dict | None = None):
    url = f"{API_BASE_URL}{endpoint}"
    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()
    return response.json()


def fetch_seguro(endpoint: str, params: dict | None = None):
    try:
        return fetch_api(endpoint, params=params)
    except requests.RequestException as exc:
        st.error(f"Erro ao consultar `{endpoint}`: {exc}")
        return None


def extrair_pontos(estado_grafico) -> list:
    if not estado_grafico:
        return []
    sel = (
        estado_grafico.get("selection")
        if isinstance(estado_grafico, dict)
        else getattr(estado_grafico, "selection", None)
    )
    if not sel:
        return []
    pts = sel.get("points") if isinstance(sel, dict) else getattr(sel, "points", [])
    return pts or []


def render_kpi_card(titulo: str, percentual: float, mulheres: int, total: int, sufixo: str, variante: str = ""):
    classe_card = f"kpi-card {variante}".strip()
    html = (
        f'<div class="{classe_card}">'
        f'<div class="kpi-title">{titulo}</div>'
        f'<div class="kpi-value">{percentual:.2f}%</div>'
        f'<div class="kpi-sub"><b>{formatar_milhar(mulheres)}</b> mulheres de {formatar_milhar(total)} {sufixo}</div>'
        f"</div>"
    )
    st.markdown(html, unsafe_allow_html=True)


def criar_grafico_rosca(titulo: str, mulheres: int, total: int, pct: float, cor_destaque: str):
    demais = max(0, total - mulheres)
    fig = go.Figure(
        data=[
            go.Pie(
                labels=["Mulheres", "Demais estudantes"],
                values=[mulheres, demais],
                hole=0.62,
                marker=dict(colors=[cor_destaque, "#E2E8F0"]),
                textinfo="none",
                hovertemplate="<b>%{label}</b><br>Total: %{value:,}<br>Proporção: %{percent}<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        title=dict(
            text=titulo,
            x=0.5,
            y=0.93,
            xanchor="center",
            yanchor="top",
            font=dict(size=13, color="#334155"),
        ),
        annotations=[
            dict(
                text=f"<b>{pct:.1f}%</b><br><span style='font-size:11px;color:#64748B'>Mulheres</span>",
                x=0.5,
                y=0.5,
                font=dict(size=18, color="#1E293B"),
                showarrow=False,
            )
        ],
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.05,
            xanchor="center",
            x=0.5,
            font=dict(size=11, color="#475569"),
        ),
        margin=dict(l=15, r=15, t=55, b=45),
        height=285,
        paper_bgcolor="#FFFFFF",
    )
    return fig


def agregar_periodo(registros: list[dict]) -> dict | None:
    if not registros:
        return None
    ing_m = sum(r["ingressantes_mulheres"] for r in registros)
    ing_t = sum(
        calcular_total(r["ingressantes_mulheres"], r["pct_ingressantes_mulheres"], r.get("total_ingressantes"))
        for r in registros
    )
    mat_m = sum(r["matriculas_mulheres"] for r in registros)
    mat_t = sum(
        calcular_total(r["matriculas_mulheres"], r["pct_matriculas_mulheres"], r.get("total_matriculas"))
        for r in registros
    )
    conc_m = sum(r["concluintes_mulheres"] for r in registros)
    conc_t = sum(
        calcular_total(r["concluintes_mulheres"], r["pct_concluintes_mulheres"], r.get("total_concluintes"))
        for r in registros
    )
    return {
        "total_ingressantes_mulheres": ing_m,
        "total_ingressantes": ing_t,
        "pct_ingressantes_mulheres": (ing_m / ing_t * 100) if ing_t else 0.0,
        "total_matriculados_mulheres": mat_m,
        "total_matriculados": mat_t,
        "pct_matriculados_mulheres": (mat_m / mat_t * 100) if mat_t else 0.0,
        "total_concluintes_mulheres": conc_m,
        "total_concluintes": conc_t,
        "pct_concluintes_mulheres": (conc_m / conc_t * 100) if conc_t else 0.0,
    }


# Barra lateral
with st.sidebar:
    st.markdown("### 👩‍💻 Tech Women Data")
    st.caption("Representatividade Feminina no Ensino Superior de TI no Brasil (INEP 2009–2024)")
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

    st.markdown("**Recorte da Série Histórica:**")
    ano_inicio, ano_fim = st.slider(
        "Selecione o intervalo de anos",
        min_value=2009,
        max_value=2024,
        value=(2009, 2024),
    )
    st.divider()

    st.markdown("**Fonte dos Dados:**")
    st.caption("Censo da Educação Superior (INEP) via Base dos Dados — Área Geral: Computação e TIC.")
    st.markdown("**Arquitetura:**")
    st.caption("MySQL Star Schema → FastAPI → Streamlit + Plotly")
    st.divider()
    st.markdown("**Links do Projeto:**")
    st.markdown(
        f"🔗 [Repositório no GitHub](https://github.com/day-om/Tech-Women-Data-API)  \n"
        f"⚡ [Swagger API (/docs)]({API_BASE_URL}/docs)"
    )

# Cabeçalho principal (renderiza imediatamente)
st.markdown(
    '<div class="hero-banner">'
    "<h1>👩‍💻 Observatório Tech Women — Ensino Superior de TI (2009–2024)</h1>"
    "<p>Análise interativa de ingresso, permanência e conclusão feminina nos cursos de Computação e TIC no Brasil.</p>"
    "</div>",
    unsafe_allow_html=True,
)

# Conexão inicial com tolerância para o cold-start do Render (até 65s)
try:
    with st.spinner("Conectando à API (no primeiro acesso pode levar até 50 segundos para iniciar o servidor)..."):
        requests.get(f"{API_BASE_URL}/", timeout=65).raise_for_status()
except requests.RequestException:
    st.warning(
        f"⚠️ Não foi possível conectar à API em `{API_BASE_URL}`. "
        "Se estiver rodando localmente, inicie o backend com `python -m uvicorn main:app --reload`."
    )
    if st.button("🔄 Tentar conectar novamente"):
        st.rerun()
    st.stop()

# Controle de seleção interativa nos gráficos
if "reset_graficos" not in st.session_state:
    st.session_state["reset_graficos"] = 0
if "uf_vol_anterior" not in st.session_state:
    st.session_state["uf_vol_anterior"] = None
if "uf_prop_anterior" not in st.session_state:
    st.session_state["uf_prop_anterior"] = None
if "uf_ativa" not in st.session_state:
    st.session_state["uf_ativa"] = None


def limpar_selecao():
    st.session_state["reset_graficos"] += 1
    st.session_state["uf_vol_anterior"] = None
    st.session_state["uf_prop_anterior"] = None
    st.session_state["uf_ativa"] = None


modo_atual = st.session_state.get("modo_visao_tempo", "Participação Feminina (%)")
key_tempo = f"evolucao_{modo_atual}_{ano_inicio}_{ano_fim}_{st.session_state['reset_graficos']}"
key_uf_vol = f"uf_volume_{st.session_state['reset_graficos']}"
key_uf_prop = f"uf_proporcao_{st.session_state['reset_graficos']}"

pts_tempo = extrair_pontos(st.session_state.get(key_tempo))
ano_sel_ativo = int(pts_tempo[0]["x"]) if pts_tempo else None

pts_uf_vol = extrair_pontos(st.session_state.get(key_uf_vol))
pts_uf_prop = extrair_pontos(st.session_state.get(key_uf_prop))
uf_vol_atual = pts_uf_vol[0]["y"] if pts_uf_vol else None
uf_prop_atual = pts_uf_prop[0]["x"] if pts_uf_prop else None

if uf_vol_atual != st.session_state["uf_vol_anterior"]:
    st.session_state["uf_vol_anterior"] = uf_vol_atual
    st.session_state["uf_ativa"] = uf_vol_atual or uf_prop_atual
elif uf_prop_atual != st.session_state["uf_prop_anterior"]:
    st.session_state["uf_prop_anterior"] = uf_prop_atual
    st.session_state["uf_ativa"] = uf_prop_atual or uf_vol_atual

uf_sel_ativa = st.session_state["uf_ativa"]

if ano_sel_ativo or uf_sel_ativa:
    filtros_txt = []
    if ano_sel_ativo:
        filtros_txt.append(f"Ano: **{ano_sel_ativo}**")
    if uf_sel_ativa:
        filtros_txt.append(f"Estado: **{uf_sel_ativa}**")
    b_col1, b_col2 = st.columns([5, 1])
    with b_col1:
        st.info(f"🎯 Filtro interativo ativo — {' | '.join(filtros_txt)}")
    with b_col2:
        st.button("Limpar seleção", on_click=limpar_selecao, use_container_width=True)

# 1. KPIs Consolidados (reagem ao clique de ano ou ao slider lateral)
kpis = fetch_seguro("/api/v1/kpis/geral")
evolucao_dados = fetch_seguro("/api/v1/metricas/evolucao-temporal") or []
rotulo_periodo = f"{ano_inicio}–{ano_fim}"

if ano_sel_ativo and evolucao_dados:
    registro_ano = next((item for item in evolucao_dados if item["year"] == ano_sel_ativo), None)
    if registro_ano:
        rotulo_periodo = f"Ano {ano_sel_ativo}"
        kpis = agregar_periodo([registro_ano])
elif (ano_inicio, ano_fim) != (2009, 2024) and evolucao_dados:
    registros_recorte = [
        item for item in evolucao_dados if ano_inicio <= item["year"] <= ano_fim
    ]
    kpis_recorte = agregar_periodo(registros_recorte)
    if kpis_recorte:
        kpis = kpis_recorte

if kpis:
    col1, col2, col3 = st.columns(3)

    with col1:
        render_kpi_card(
            f"Ingressantes Mulheres ({rotulo_periodo})",
            kpis["pct_ingressantes_mulheres"],
            kpis["total_ingressantes_mulheres"],
            kpis["total_ingressantes"],
            "ingressantes",
        )

    with col2:
        render_kpi_card(
            f"Matrículas Ativas Mulheres ({rotulo_periodo})",
            kpis["pct_matriculados_mulheres"],
            kpis["total_matriculados_mulheres"],
            kpis["total_matriculados"],
            "matrículas",
            variante="pink",
        )

    with col3:
        render_kpi_card(
            f"Concluintes Mulheres ({rotulo_periodo})",
            kpis["pct_concluintes_mulheres"],
            kpis["total_concluintes_mulheres"],
            kpis["total_concluintes"],
            "concluintes",
            variante="indigo",
        )

    st.markdown("<br>", unsafe_allow_html=True)
    r_col1, r_col2, r_col3 = st.columns(3)

    with r_col1:
        fig_r1 = criar_grafico_rosca(
            f"Proporção de<br>Ingressantes ({rotulo_periodo})",
            kpis["total_ingressantes_mulheres"],
            kpis["total_ingressantes"],
            kpis["pct_ingressantes_mulheres"],
            "#9333EA",
        )
        st.plotly_chart(fig_r1, use_container_width=True, key=f"rosca_ing_{rotulo_periodo}")

    with r_col2:
        fig_r2 = criar_grafico_rosca(
            f"Proporção de<br>Matrículas Ativas ({rotulo_periodo})",
            kpis["total_matriculados_mulheres"],
            kpis["total_matriculados"],
            kpis["pct_matriculados_mulheres"],
            "#DB2777",
        )
        st.plotly_chart(fig_r2, use_container_width=True, key=f"rosca_mat_{rotulo_periodo}")

    with r_col3:
        fig_r3 = criar_grafico_rosca(
            f"Proporção de<br>Concluintes ({rotulo_periodo})",
            kpis["total_concluintes_mulheres"],
            kpis["total_concluintes"],
            kpis["pct_concluintes_mulheres"],
            "#4F46E5",
        )
        st.plotly_chart(fig_r3, use_container_width=True, key=f"rosca_conc_{rotulo_periodo}")

st.markdown("<br>", unsafe_allow_html=True)

# 2. Abas Analíticas
tab_tempo, tab_estados, tab_cursos, tab_filtro = st.tabs(
    [
        "📈 Evolução Temporal (2009–2024)",
        "🗺️ Panorama por Estado (UF)",
        "🎓 Ranking de Cursos",
        "🔎 Explorador Dinâmico",
    ]
)

# --- ABA 1: EVOLUÇÃO TEMPORAL ---
with tab_tempo:
    st.subheader("Trajetória da Participação Feminina ao Longo dos Anos")
    df_tempo = pd.DataFrame(evolucao_dados)

    if not df_tempo.empty:
        df_tempo = df_tempo[
            (df_tempo["year"] >= ano_inicio) & (df_tempo["year"] <= ano_fim)
        ].copy()

        modo_visao = st.radio(
            "Selecione a métrica de visualização:",
            options=["Participação Feminina (%)", "Volume Absoluto de Mulheres"],
            horizontal=True,
            key="modo_visao_tempo",
        )

        fig_linha = go.Figure()

        if modo_visao == "Participação Feminina (%)":
            fig_linha.add_trace(
                go.Scatter(
                    x=df_tempo["year"],
                    y=df_tempo["pct_ingressantes_mulheres"],
                    mode="lines+markers+text",
                    name="Ingressantes (%)",
                    text=[f"{v:.1f}%" for v in df_tempo["pct_ingressantes_mulheres"]],
                    textposition="top center",
                    line=dict(color="#9333EA", width=3),
                    marker=dict(size=8),
                )
            )
            fig_linha.add_trace(
                go.Scatter(
                    x=df_tempo["year"],
                    y=df_tempo["pct_matriculas_mulheres"],
                    mode="lines+markers",
                    name="Matrículas Ativas (%)",
                    line=dict(color="#DB2777", width=3),
                    marker=dict(size=8),
                )
            )
            fig_linha.add_trace(
                go.Scatter(
                    x=df_tempo["year"],
                    y=df_tempo["pct_concluintes_mulheres"],
                    mode="lines+markers",
                    name="Concluintes (%)",
                    line=dict(color="#4F46E5", width=3, dash="dot"),
                    marker=dict(size=8),
                )
            )
            fig_linha.update_yaxes(title="Participação Feminina (%)", range=[10, 24])
            texto_destaque = (
                "**Destaque da Série Percentual:** Os indicadores formam uma curva em 'U' — após atingirem o menor patamar "
                "entre 2017 e 2018 (~13,2%), todos os estágios iniciaram recuperação contínua, alcançando recorde histórico em 2024 "
                "(**21,30%** de ingressantes mulheres)."
            )
        else:
            fig_linha.add_trace(
                go.Scatter(
                    x=df_tempo["year"],
                    y=df_tempo["ingressantes_mulheres"],
                    mode="lines+markers",
                    name="Ingressantes Mulheres",
                    customdata=[formatar_milhar(v) for v in df_tempo["ingressantes_mulheres"]],
                    hovertemplate="Ingressantes: <b>%{customdata}</b><extra></extra>",
                    line=dict(color="#9333EA", width=3),
                    marker=dict(size=8),
                )
            )
            fig_linha.add_trace(
                go.Scatter(
                    x=df_tempo["year"],
                    y=df_tempo["matriculas_mulheres"],
                    mode="lines+markers+text",
                    name="Matrículas Ativas Mulheres",
                    text=[
                        formatar_milhar(v) if ano in (2009, 2017, 2020, 2024) else ""
                        for ano, v in zip(df_tempo["year"], df_tempo["matriculas_mulheres"])
                    ],
                    textposition="top center",
                    customdata=[formatar_milhar(v) for v in df_tempo["matriculas_mulheres"]],
                    hovertemplate="Matrículas Ativas: <b>%{customdata}</b><extra></extra>",
                    line=dict(color="#DB2777", width=3),
                    marker=dict(size=8),
                )
            )
            fig_linha.add_trace(
                go.Scatter(
                    x=df_tempo["year"],
                    y=df_tempo["concluintes_mulheres"],
                    mode="lines+markers",
                    name="Concluintes Mulheres",
                    customdata=[formatar_milhar(v) for v in df_tempo["concluintes_mulheres"]],
                    hovertemplate="Concluintes: <b>%{customdata}</b><extra></extra>",
                    line=dict(color="#4F46E5", width=3, dash="dot"),
                    marker=dict(size=8),
                )
            )
            fig_linha.update_yaxes(title="Total de Mulheres (Estudantes)")
            texto_destaque = (
                "**Destaque do Volume Absoluto:** Mesmo durante os anos de queda na proporção relativa, o número absoluto "
                "de mulheres na área de TI cresceu de forma consistente — saltando para **153.931 matrículas ativas** e "
                "**104.176 novas ingressantes** apenas em 2024."
            )

        fig_linha.update_layout(
            clickmode="event+select",
            xaxis=dict(title="Ano do Censo", tickmode="linear", dtick=1),
            hovermode="x unified",
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=450,
            margin=dict(l=20, r=20, t=40, b=20),
        )

        st.caption("💡 Dica: clique em qualquer ponto de ano no gráfico para atualizar os cartões de KPI e roscas acima.")

        st.plotly_chart(
            fig_linha,
            use_container_width=True,
            on_select="rerun",
            selection_mode="points",
            key=key_tempo,
        )

        if len(df_tempo) >= 2:
            ini = df_tempo.iloc[0]
            fim = df_tempo.iloc[-1]
            diff_pct = fim["pct_ingressantes_mulheres"] - ini["pct_ingressantes_mulheres"]
            sinal = "+" if diff_pct >= 0 else ""
            st.info(
                f"**Resumo do Recorte ({int(ini['year'])}–{int(fim['year'])}):** "
                f"A participação feminina entre ingressantes passou de **{ini['pct_ingressantes_mulheres']:.2f}%** "
                f"para **{fim['pct_ingressantes_mulheres']:.2f}%** (**{sinal}{diff_pct:.2f} p.p.**), "
                f"somando **{formatar_milhar(fim['matriculas_mulheres'])}** matrículas ativas em {int(fim['year'])}."
            )
        else:
            st.info(texto_destaque)

# --- ABA 2: ESTADOS (UF) ---
estados_dados = fetch_seguro("/api/v1/metricas/estados") or []
df_estados = pd.DataFrame(estados_dados)

with tab_estados:
    st.subheader("Distribuição Geográfica: Volume vs. Permanência Feminina")
    st.caption("💡 Dica: clique na barra de qualquer estado para ver seus indicadores detalhados.")

    if not df_estados.empty:
        if uf_sel_ativa:
            dados_uf = df_estados[df_estados["state_uf"] == uf_sel_ativa]
            if not dados_uf.empty:
                row_uf = dados_uf.iloc[0]
                u1, u2, u3, u4 = st.columns(4)
                u1.metric("Estado Selecionado", uf_sel_ativa)
                u2.metric("Total de Matrículas", formatar_milhar(row_uf["total_matriculas"]))
                u3.metric(
                    "Mulheres Matriculadas",
                    f"{row_uf['pct_mulheres_matriculas']:.2f}%",
                    f"{formatar_milhar(row_uf['matriculas_mulheres'])} alunas",
                )
                u4.metric("Taxa de Concluintes", f"{row_uf['pct_mulheres_concluintes']:.2f}%")
                st.markdown("<br>", unsafe_allow_html=True)

        col_uf1, col_uf2 = st.columns(2, gap="medium")

        with col_uf1:
            top_vol = (
                df_estados.sort_values(by="total_matriculas", ascending=False)
                .head(10)
                .sort_values(by="total_matriculas", ascending=True)
                .copy()
            )
            top_vol["demais_matriculas"] = top_vol["total_matriculas"] - top_vol["matriculas_mulheres"]

            def fmt_curto(valor: float) -> str:
                if valor >= 1_000_000:
                    return f"{valor / 1_000_000:.2f} Mi".replace(".", ",")
                return f"{round(valor / 1_000):,} mil".replace(",", ".")

            rotulos = [
                f"  <b>{fmt_curto(tot)}</b> <span style='color:#DB2777'>({fmt_curto(mul)} mul.)</span>"
                for tot, mul in zip(top_vol["total_matriculas"], top_vol["matriculas_mulheres"])
            ]

            fig_vol = go.Figure()
            fig_vol.add_trace(
                go.Bar(
                    y=top_vol["state_uf"],
                    x=top_vol["matriculas_mulheres"],
                    name="Mulheres",
                    orientation="h",
                    marker_color="#DB2777",
                    hovertemplate="Mulheres: <b>%{x:,}</b><extra></extra>",
                )
            )
            fig_vol.add_trace(
                go.Bar(
                    y=top_vol["state_uf"],
                    x=top_vol["demais_matriculas"],
                    name="Demais estudantes",
                    orientation="h",
                    marker_color="#CBD5E1",
                    hovertemplate="Demais estudantes: <b>%{x:,}</b><extra></extra>",
                )
            )
            fig_vol.add_trace(
                go.Scatter(
                    y=top_vol["state_uf"],
                    x=top_vol["total_matriculas"],
                    mode="text",
                    text=rotulos,
                    textposition="middle right",
                    textfont=dict(size=11, color="#1E293B"),
                    showlegend=False,
                    hoverinfo="skip",
                )
            )
            fig_vol.update_layout(
                title=dict(
                    text="Top 10 Estados: Volume de Matrículas (Total vs. Mulheres)",
                    x=0.04,
                    y=0.95,
                    xanchor="left",
                    yanchor="top",
                    font=dict(size=15, color="#1E293B"),
                ),
                barmode="stack",
                hovermode="y unified",
                clickmode="event+select",
                yaxis=dict(title=""),
                xaxis=dict(
                    title=dict(text="Total de Matrículas", standoff=14),
                    range=[0, top_vol["total_matriculas"].max() * 1.48],
                ),
                legend=dict(
                    orientation="h",
                    traceorder="normal",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                ),
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
                margin=dict(l=45, r=30, t=90, b=60),
                height=470,
            )
            st.plotly_chart(
                fig_vol,
                use_container_width=True,
                on_select="rerun",
                selection_mode="points",
                key=key_uf_vol,
            )

        with col_uf2:
            top_prop = df_estados.sort_values(by="pct_mulheres_matriculas", ascending=False).head(10).copy()
            max_y = max(
                top_prop["pct_mulheres_matriculas"].max(),
                top_prop["pct_mulheres_concluintes"].max(),
            )

            fig_prop = go.Figure()
            fig_prop.add_trace(
                go.Bar(
                    x=top_prop["state_uf"],
                    y=top_prop["pct_mulheres_matriculas"],
                    name="Matrículas (%)",
                    text=[f"{v:.1f}%" for v in top_prop["pct_mulheres_matriculas"]],
                    textposition="outside",
                    marker_color="#DB2777",
                )
            )
            fig_prop.add_trace(
                go.Bar(
                    x=top_prop["state_uf"],
                    y=top_prop["pct_mulheres_concluintes"],
                    name="Concluintes (%)",
                    text=[f"{v:.1f}%" for v in top_prop["pct_mulheres_concluintes"]],
                    textposition="outside",
                    marker_color="#4F46E5",
                )
            )
            fig_prop.update_layout(
                title=dict(
                    text="Top 10 Estados: Matrículas vs. Concluintes (%)",
                    x=0.04,
                    y=0.95,
                    xanchor="left",
                    yanchor="top",
                    font=dict(size=15, color="#1E293B"),
                ),
                barmode="group",
                clickmode="event+select",
                yaxis=dict(
                    title=dict(text="Participação Feminina (%)", standoff=12),
                    range=[0, max_y * 1.24],
                ),
                xaxis=dict(title=dict(text="Estado (UF)", standoff=14)),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                ),
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
                margin=dict(l=65, r=30, t=90, b=60),
                height=470,
            )
            st.plotly_chart(
                fig_prop,
                use_container_width=True,
                on_select="rerun",
                selection_mode="points",
                key=key_uf_prop,
            )

# --- ABA 3: CURSOS ---
with tab_cursos:
    st.subheader("Ranking de Cursos: Matrículas vs. Concluintes (%)")
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        min_mat = st.slider("Volume mínimo acumulado de matrículas", 0, 50000, 5000, step=1000)
    with f_col2:
        limite_cursos = st.slider("Quantidade de cursos no ranking", 5, 30, 10)

    cursos = fetch_seguro(
        "/api/v1/metricas/cursos",
        params={"min_matriculas": min_mat, "limit": limite_cursos},
    )
    df_cursos = pd.DataFrame(cursos or [])

    if not df_cursos.empty:
        df_cursos_plot = df_cursos.sort_values(by="pct_mulheres_matriculas", ascending=True)
        max_x = max(
            df_cursos_plot["pct_mulheres_matriculas"].max(),
            df_cursos_plot["pct_mulheres_concluintes"].max(),
        )

        fig_cursos = go.Figure()
        fig_cursos.add_trace(
            go.Bar(
                y=df_cursos_plot["course_name"],
                x=df_cursos_plot["pct_mulheres_matriculas"],
                name="Matrículas (%)",
                orientation="h",
                text=[f"{v:.1f}%" for v in df_cursos_plot["pct_mulheres_matriculas"]],
                textposition="outside",
                marker_color="#DB2777",
            )
        )
        fig_cursos.add_trace(
            go.Bar(
                y=df_cursos_plot["course_name"],
                x=df_cursos_plot["pct_mulheres_concluintes"],
                name="Concluintes (%)",
                orientation="h",
                text=[f"{v:.1f}%" for v in df_cursos_plot["pct_mulheres_concluintes"]],
                textposition="outside",
                marker_color="#4F46E5",
            )
        )
        fig_cursos.update_layout(
            barmode="group",
            xaxis=dict(title="Participação Feminina (%)", range=[0, max_x * 1.2]),
            yaxis=dict(title=""),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            height=max(460, limite_cursos * 48),
            margin=dict(l=10, r=20, t=45, b=20),
        )
        st.plotly_chart(fig_cursos, use_container_width=True, key=f"cursos_{min_mat}_{limite_cursos}")
    else:
        st.warning("Nenhum curso encontrado com esse filtro de matrículas mínimas.")

# --- ABA 4: EXPLORADOR DINÂMICO ---
with tab_filtro:
    st.subheader("Consulta Dinâmica na API")
    c1, c2, c3, c4 = st.columns([1, 1, 2, 1])

    opcoes_uf = ["Todas"] + (
        sorted(df_estados["state_uf"].dropna().unique().tolist()) if not df_estados.empty else []
    )

    with c1:
        usar_ano = st.checkbox("Filtrar por ano", value=True)
        ano_sel = st.number_input("Ano", min_value=2009, max_value=2024, value=2024, disabled=not usar_ano)
    with c2:
        uf_sel = st.selectbox("Estado (UF)", options=opcoes_uf)
    with c3:
        curso_sel = st.text_input("Trecho do nome do curso", placeholder="Ex: CIENCIA, DADOS, ADS").strip()
    with c4:
        limit_sel = st.number_input("Limite", min_value=1, max_value=500, value=50)

    query_params = {"limit": limit_sel}
    if usar_ano:
        query_params["ano"] = ano_sel
    if uf_sel != "Todas":
        query_params["uf"] = uf_sel
    if curso_sel:
        query_params["curso"] = curso_sel

    filtrados = fetch_seguro("/api/v1/metricas/filtrar", params=query_params)
    df_filtrados = pd.DataFrame(filtrados or [])

    if not df_filtrados.empty:
        st.caption(f"Exibindo **{len(df_filtrados)}** registros retornados pela API.")
        st.dataframe(df_filtrados, use_container_width=True, hide_index=True)
        csv = df_filtrados.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Baixar resultado filtrado (CSV)",
            data=csv,
            file_name="tech_women_filtrado.csv",
            mime="text/csv",
        )
    else:
        st.info("Nenhum registro encontrado para essa combinação de filtros.")