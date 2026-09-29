import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Fintech Analytics",
    page_icon="📊",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent
TRANSACOES_FILE = BASE_DIR / "transacoes.csv"
COTACOES_FILE = BASE_DIR / "cotacoes.csv"

# Dicionário solicitado no enunciado.
risco_dict = {
    "C100": "Baixo",
    "C101": "Alto",
    "C102": "Médio",
    "C103": "Baixo",
    "C104": "Alto",
}


@st.cache_data
def carregar_transacoes():
    """Carrega, limpa e transforma o arquivo de transações."""
    df = pd.read_csv(
        TRANSACOES_FILE,
        encoding="latin1"
    )

    # Conversão para datetime64[ns] antes da localização do fuso.
    df["data_transacao"] = pd.to_datetime(
        df["data_transacao"],
        errors="coerce"
    )

    # Imputação da mediana de valor por estado.
    medianas_estado = df.groupby("estado_cliente")["valor"].transform("median")
    df["valor"] = df["valor"].fillna(medianas_estado)

    # Rastreabilidade.
    df["plataforma"] = "Mobile"

    # Fuso horário America/Sao_Paulo.
    df["data_transacao"] = df["data_transacao"].dt.tz_localize(
        "America/Sao_Paulo"
    )

    # Informações temporais via .dt.
    df["dia_semana"] = df["data_transacao"].dt.day_name()
    df["mes"] = df["data_transacao"].dt.month

    # Remove duplicidades mantendo a primeira ocorrência.
    df = df.drop_duplicates(keep="first").copy()

    # Cruzamento com risco usando .map().
    df["nivel_risco"] = df["id_cliente"].map(risco_dict)

    # Z-Score por estado, totalmente vetorizado.
    df["media_estado"] = df.groupby("estado_cliente")["valor"].transform("mean")
    df["desvio_estado"] = df.groupby("estado_cliente")["valor"].transform("std")

    # std(ddof=0) é usado para deixar o cálculo consistente com a definição
    # populacional do Z-Score. O desvio zero é tratado como NaN.
    df["desvio_estado_pop"] = df.groupby("estado_cliente")["valor"].transform(
        lambda s: s.std(ddof=0)
    )
    df["z_score"] = (
        (df["valor"] - df["media_estado"])
        / df["desvio_estado_pop"].replace(0, np.nan)
    )

    df["data_dia"] = df["data_transacao"].dt.floor("D")

    return df


@st.cache_data
def carregar_cotacoes():
    if not COTACOES_FILE.exists():
        return pd.DataFrame()

    df = pd.read_csv(COTACOES_FILE, encoding="utf-8")
    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    return df


def filtro_setembro_sp_rj(df):
    """Filtro vetorizado obrigatório com operadores bitwise."""
    return df[
        (df["mes"] == 9)
        & (
            (df["estado_cliente"] == "SP")
            | (df["estado_cliente"] == "RJ")
        )
        & (df["valor"] > 5000)
    ].copy()


def tabela_pivot_risco(df):
    """Tabela dinâmica por mês e nível de risco com margens."""
    return pd.pivot_table(
        df,
        index="mes",
        columns="nivel_risco",
        values="valor",
        aggfunc="sum",
        margins=True,
        margins_name="Total"
    )


def calcular_anomalias(df):
    """Seleciona potenciais anomalias sem laços for."""
    return df[df["z_score"] > 2.5].copy()


def grafico_diario(df):
    """Gráfico OO Matplotlib: total diário + média móvel de 7 dias."""
    diario = (
        df.groupby("data_dia", as_index=True)["valor"]
        .sum()
        .sort_index()
    )
    media_movel = diario.rolling(7).mean()

    fig, ax = plt.subplots(figsize=(12, 4.8))
    ax.plot(diario.index, diario.values, label="Valor total diário")
    ax.plot(media_movel.index, media_movel.values, label="Média móvel (7 dias)")

    ax.set_ylim(bottom=0)
    ax.set_title("Valor total de transações e média móvel de 7 dias")
    ax.set_xlabel("Data")
    ax.set_ylabel("Valor (R$)")
    ax.legend()
    ax.grid(alpha=0.25)
    fig.autofmt_xdate()
    fig.tight_layout()

    return fig


def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


st.title("📊 Fintech Analytics")
st.caption("Pipeline de ingestão, limpeza, agregação, detecção de anomalias e visualização.")

if not TRANSACOES_FILE.exists():
    st.error(
        "Arquivo transacoes.csv não encontrado. "
        "Execute primeiro `python criar_dados.py` na pasta do projeto."
    )
    st.stop()

df = carregar_transacoes()
cotacoes = carregar_cotacoes()

# Filtro obrigatório do exercício.
df_filtrado = filtro_setembro_sp_rj(df)

# Anomalias.
anomalias = calcular_anomalias(df)

# Pivot.
pivot = tabela_pivot_risco(df)

# KPIs.
col1, col2, col3, col4 = st.columns(4)
col1.metric("Transações válidas", f"{len(df):,}".replace(",", "."))
col2.metric("Faturamento total", formatar_moeda(df["valor"].sum()))
col3.metric("Set/ SP-RJ > R$ 5 mil", f"{len(df_filtrado):,}".replace(",", "."))
col4.metric("Potenciais anomalias", f"{len(anomalias):,}".replace(",", "."))

st.divider()

tab1, tab2, tab3, tab4 = st.tabs(
    ["📈 Visão geral", "🔎 Filtro do exercício", "🚨 Anomalias", "📋 Dados e pivot"]
)

with tab1:
    st.subheader("Desempenho diário")
    st.pyplot(grafico_diario(df), use_container_width=True)

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Valor por estado")
        por_estado = (
            df.groupby("estado_cliente", as_index=False)["valor"]
            .sum()
            .sort_values("valor", ascending=False)
            .set_index("estado_cliente")
        )
        st.bar_chart(por_estado)

    with c2:
        st.subheader("Transações por nível de risco")
        por_risco = (
            df["nivel_risco"]
            .value_counts()
            .rename_axis("nivel_risco")
            .to_frame("quantidade")
        )
        st.bar_chart(por_risco)

    if not cotacoes.empty:
        st.subheader("Cotação USD — arquivo auxiliar")
        cot = cotacoes.set_index("data")["cotacao_usd"]
        st.line_chart(cot)

with tab2:
    st.subheader("Setembro + SP/RJ + valor > R$ 5.000")
    st.write(
        "Filtro vetorizado aplicado com `&` e `|`, conforme solicitado no exercício."
    )
    st.dataframe(
        df_filtrado[
            [
                "id_cliente",
                "data_transacao",
                "valor",
                "origem",
                "estado_cliente",
                "plataforma",
                "nivel_risco",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.metric("Valor total do filtro", formatar_moeda(df_filtrado["valor"].sum()))

with tab3:
    st.subheader("Potenciais anomalias / fraudes")
    st.write("Critério: Z-Score > 2,5 calculado separadamente por estado.")

    st.dataframe(
        anomalias[
            [
                "id_cliente",
                "data_transacao",
                "valor",
                "estado_cliente",
                "nivel_risco",
                "z_score",
            ]
        ].sort_values("z_score", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

    if not anomalias.empty:
        st.bar_chart(
            anomalias.groupby("estado_cliente")["valor"]
            .sum()
            .sort_values(ascending=False)
        )

with tab4:
    st.subheader("Tabela dinâmica — valor por mês e nível de risco")
    st.dataframe(
        pivot.style.format("{:,.2f}"),
        use_container_width=True
    )

    st.subheader("Dados processados")
    st.dataframe(df, use_container_width=True, hide_index=True)

st.sidebar.header("Pipeline")
st.sidebar.success("✓ CSV lido com encoding latin1")
st.sidebar.success("✓ NaN imputado pela mediana por estado")
st.sidebar.success("✓ Fuso America/Sao_Paulo aplicado")
st.sidebar.success("✓ Duplicidades removidas")
st.sidebar.success("✓ Risco atribuído com .map()")
st.sidebar.success("✓ Z-Score vetorizado")
st.sidebar.success("✓ Filtro bitwise aplicado")
