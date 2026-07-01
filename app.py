"""
Dashboard de Tesouraria Corporativa
Análises executivas para decisão rápida
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO
import os
from datetime import datetime, timedelta

ARQUIVO_MANUAL = "dados_manuais.csv"
ARQUIVO_ORCADO = "orcamento.csv"

st.set_page_config(
    page_title="Tesouraria Corporativa",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== PALETA MINIMALISTA =====
CORES = {
    'risco': '#DC2626',        # Vermelho — apenas para alertas
    'neutro': '#6B7280',       # Cinza — dados normais
    'background': '#F9FAFB',   # Fundo claro
    'texto': '#1F2937',        # Texto escuro
}

# ===== ESTILOS MINIMALISTAS =====
st.markdown("""
<style>
    /* Fundo limpo */
    body {
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #F9FAFB;
    }

    /* Tipografia */
    h1, h2, h3 {
        color: #1F2937;
        font-weight: 600;
        letter-spacing: -0.5px;
    }

    /* Métrica minimalista */
    .stMetricValue {
        font-size: 32px;
        font-weight: 700;
        color: #1F2937;
    }

    .stMetricLabel {
        color: #6B7280;
        font-size: 13px;
        font-weight: 500;
    }

    /* Gráficos: fundo branco puro */
    .stPlotlyChart {
        background: white;
        border-radius: 2px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }

    /* Tabelas */
    .dataframe { color: #1F2937; }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# FUNÇÕES DE DADOS
# ============================================================================

def carregar_csv(caminho):
    """Carrega dados do Sienge."""
    try:
        df = pd.read_csv(caminho)
        df['Data'] = pd.to_datetime(df['Data'])
        df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
        return df
    except:
        return None

def carregar_dados_manuais():
    """Carrega entradas manuais persistidas."""
    if os.path.exists(ARQUIVO_MANUAL):
        try:
            df = pd.read_csv(ARQUIVO_MANUAL)
            df['Data'] = pd.to_datetime(df['Data'])
            df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
            return df
        except:
            return pd.DataFrame()
    return pd.DataFrame()

def consolidar_dados(df_sienge, df_manual):
    """Consolida Sienge + entrada manual."""
    if df_manual is not None and not df_manual.empty:
        return pd.concat([df_sienge, df_manual], ignore_index=True)
    return df_sienge

def calcular_metricas_essenciais(df):
    """Calcula métricas críticas para CFO."""
    if df is None or df.empty:
        return None

    total_receitas = df[df['Valor'] > 0]['Valor'].sum()
    total_despesas = abs(df[df['Valor'] < 0]['Valor'].sum())
    saldo = total_receitas - total_despesas

    # Burn rate
    mes_min = df['Data'].min().year
    mes_max = df['Data'].max().year
    dias = (df['Data'].max() - df['Data'].min()).days + 1
    burn_rate_dia = abs(saldo) / max(dias, 1)
    burn_rate_mes = burn_rate_dia * 30

    # Runway (meses até quebra)
    caixa_atual = saldo
    runway = caixa_atual / max(burn_rate_mes, 0.01) if burn_rate_mes > 0 else 999

    # Status de risco (apenas para métrica, sem alerta visual)
    if runway < 2:
        cor_status = CORES['risco']
    else:
        cor_status = CORES['neutro']

    # Maior despesa
    maior_despesa_linha = df[df['Valor'] < 0].nsmallest(1, 'Valor')
    if not maior_despesa_linha.empty:
        maior_despesa = maior_despesa_linha.iloc[0]
        maior_despesa_texto = f"{maior_despesa['DescricaoLinha']}: R$ {abs(maior_despesa['Valor']):,.0f}"
    else:
        maior_despesa_texto = "N/A"

    return {
        'saldo': saldo,
        'receitas': total_receitas,
        'despesas': total_despesas,
        'burn_rate_dia': burn_rate_dia,
        'burn_rate_mes': burn_rate_mes,
        'runway': runway,
        'status': status,
        'cor_status': cor_status,
        'maior_despesa': maior_despesa_texto,
    }

def criar_tabela_por_mes(df):
    """Cria tabela mês × categoria com saldo acumulado."""
    df_piv = df.copy()
    df_piv['Mes'] = df_piv['Data'].dt.to_period('M')
    df_piv['Mes_str'] = df_piv['Data'].dt.strftime('%b/%y')

    # Pivotar por categoria
    tabela = df_piv.pivot_table(
        index='DescricaoLinha',
        columns='Mes',
        values='Valor',
        aggfunc='sum',
        fill_value=0
    )

    # Adicionar total
    tabela['TOTAL'] = tabela.sum(axis=1)
    return tabela.sort_values('TOTAL')

def criar_waterfall(df):
    """Cria Waterfall: Receitas - Despesas = Saldo."""
    receitas = df[df['Valor'] > 0]['Valor'].sum()
    despesas_por_categoria = df[df['Valor'] < 0].groupby('Categoria')['Valor'].sum().sort_values()

    # Construir dados para waterfall
    nomes = ['Saldo Inicial: R$ 0']
    valores = [0]
    tipos = ['absolute']

    nomes.append(f"Receitas (+{receitas:,.0f})")
    valores.append(receitas)
    tipos.append('relative')

    for cat, val in despesas_por_categoria.items():
        nomes.append(f"{cat} ({val:,.0f})")
        valores.append(val)
        tipos.append('relative')

    saldo_final = receitas + despesas_por_categoria.sum()
    nomes.append(f"Saldo Final: {saldo_final:,.0f}")
    valores.append(0)
    tipos.append('total')

    fig = go.Figure(go.Waterfall(
        name='Fluxo de Caixa',
        orientation='v',
        x=nomes,
        y=valores,
        connector={'line': {'color': CORES['neutro']}},
        increasing={'marker': {'color': CORES['neutro']}},  # Receitas em cinza
        decreasing={'marker': {'color': CORES['risco']}},   # Despesas em vermelho (alerta)
        totals={'marker': {'color': '#111827'}},            # Total em preto
    ))

    fig.update_layout(
        title='Geração e Consumo de Caixa',
        height=400,
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(family='Segoe UI', size=11, color='#333'),
    )

    return fig

def criar_pareto(df):
    """Cria gráfico Pareto: Top despesas com % acumulada."""
    despesas = df[df['Valor'] < 0].copy()
    despesas['Valor_abs'] = abs(despesas['Valor'])

    top10 = despesas.groupby('DescricaoLinha')['Valor_abs'].sum().nlargest(10).reset_index()
    top10 = top10.sort_values('Valor_abs', ascending=True)

    total_despesas = despesas['Valor_abs'].sum()
    top10['% do Total'] = (top10['Valor_abs'] / total_despesas * 100).round(1)
    top10['% Acumulada'] = top10['% do Total'].cumsum().round(1)

    fig = go.Figure()

    # Barras em cinza
    fig.add_trace(go.Bar(
        y=top10['DescricaoLinha'],
        x=top10['Valor_abs'],
        orientation='h',
        name='Consumo',
        marker=dict(color=CORES['neutro']),
        text=top10['% do Total'].apply(lambda x: f"{x:.0f}%"),
        textposition='outside',
    ))

    # Linha de % acumulada em cinza escuro
    fig.add_trace(go.Scatter(
        y=top10['DescricaoLinha'],
        x=top10['% Acumulada'] * total_despesas / 100,
        mode='lines+markers',
        name='% Acumulada',
        line=dict(color='#374151', width=2),
        marker=dict(size=8),
        yaxis='y',
        xaxis='x2',
    ))

    fig.update_layout(
        title='Pareto: Top 10 Consumidores de Caixa (Princípio 80/20)',
        height=400,
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor='white',
        plot_bgcolor='white',
        hovermode='closest',
        xaxis=dict(title='R$'),
        yaxis=dict(title=''),
        font=dict(family='Segoe UI', size=11, color='#333'),
        showlegend=False,
    )

    return fig

def criar_heatmap_sazonalidade(df):
    """Heatmap: intensidade de gasto por mês."""
    df_piv = df.copy()
    df_piv['Mes'] = df_piv['Data'].dt.to_period('M')

    tabela = df_piv.pivot_table(
        index='DescricaoLinha',
        columns='Mes',
        values='Valor',
        aggfunc='sum',
        fill_value=0
    )

    # Normalizar para intensidade (-1 a 1)
    tabela_norm = tabela.copy()
    for col in tabela_norm.columns:
        max_val = tabela[col].abs().max()
        if max_val > 0:
            tabela_norm[col] = tabela[col] / max_val

    fig = go.Figure(data=go.Heatmap(
        z=tabela.values,
        x=[str(c) for c in tabela.columns],
        y=tabela.index,
        colorscale='Greys',  # Escala cinza — minimalista
        hovertemplate='<b>%{y}</b><br>%{x}<br>R$ %{z:,.0f}<extra></extra>',
    ))

    fig.update_layout(
        title='Sazonalidade: Padrões Invisíveis de Gasto',
        height=400,
        xaxis_title='Período',
        yaxis_title='Categoria',
        margin=dict(l=150, r=0, t=30, b=0),
        paper_bgcolor='white',
    )

    return fig

def criar_variance_analysis(df, df_orcado=None):
    """Compara Realizado vs. Orçado."""
    realizado = df[df['Valor'] < 0].groupby('DescricaoLinha')['Valor'].sum().abs()

    if df_orcado is None or df_orcado.empty:
        # Sem orçado, mostrar apenas ranking
        df_var = realizado.reset_index()
        df_var.columns = ['Categoria', 'Realizado']
        df_var['Status'] = '📊'
    else:
        orcado = df_orcado.groupby('DescricaoLinha')['Valor'].sum().abs()
        df_var = pd.DataFrame({
            'Categoria': realizado.index,
            'Orçado': realizado.index.map(lambda x: orcado.get(x, 0)),
            'Realizado': realizado.values
        })
        df_var['Diferença'] = df_var['Realizado'] - df_var['Orçado']
        df_var['Diferença %'] = (df_var['Diferença'] / df_var['Orçado'] * 100).round(1)

        # Destacar desvios > 10%
        df_var['Status'] = df_var['Diferença %'].apply(
            lambda x: '🔴' if abs(x) > 10 else ('🟡' if abs(x) > 5 else '🟢')
        )

    return df_var.sort_values('Realizado', ascending=False)

# ============================================================================
# INTERFACE
# ============================================================================

# Header
st.markdown("# 💰 Tesouraria Corporativa")
st.markdown("---")

# Sidebar: Upload e dados
with st.sidebar:
    st.markdown("## ⚙️ Dados")

    csv_padrao = os.path.join(os.path.dirname(__file__), "output", "fc_dados.csv")
    if os.path.exists(csv_padrao):
        usar_padrao = st.checkbox("Usar dados padrão", value=True)
        caminho_csv = csv_padrao if usar_padrao else st.file_uploader("Selecione CSV", type="csv")
    else:
        caminho_csv = st.file_uploader("Selecione CSV", type="csv")

    df_sienge = None
    if caminho_csv is not None:
        if isinstance(caminho_csv, str):
            df_sienge = carregar_csv(caminho_csv)
        else:
            df_sienge = carregar_csv(caminho_csv.name)

    if df_sienge is not None:
        df_manual = carregar_dados_manuais()
        df = consolidar_dados(df_sienge, df_manual)

        st.success(f"✅ {len(df)} transações carregadas")
        st.caption(f"{df['Data'].min().strftime('%d/%m/%y')} a {df['Data'].max().strftime('%d/%m/%y')}")
    else:
        st.warning("Carregue um CSV")
        df = None

# ============================================================================
# DASHBOARD PRINCIPAL
# ============================================================================

if df is not None and not df.empty:
    # ===== EXECUTIVE SUMMARY (15 segundos) =====
    metricas = calcular_metricas_essenciais(df)

    st.markdown("## 📊 Executive Summary")

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric(
            "Caixa Atual",
            f"R$ {metricas['saldo']:,.0f}",
            delta=None,
        )

    with col2:
        st.metric(
            "Burn Rate",
            f"R$ {metricas['burn_rate_mes']:,.0f}/mês",
            delta=None,
        )

    with col3:
        st.metric(
            "Runway",
            f"{metricas['runway']:.1f} meses",
            delta=metricas['status'],
        )

    with col4:
        st.metric(
            "Receitas",
            f"R$ {metricas['receitas']:,.0f}",
            delta=None,
        )

    with col5:
        st.metric(
            "Despesas",
            f"R$ {metricas['despesas']:,.0f}",
            delta=None,
        )

    with col6:
        st.metric("Status", "Operacional" if cor_status == CORES['neutro'] else "Alerta", delta=None)

    st.markdown("---")

    # ===== ABAS: GRÁFICOS vs DETALHES =====
    tab_graficos, tab_detalhes = st.tabs(["📊 Gráficos", "📋 Detalhes"])

    with tab_graficos:
        # Waterfall + Pareto
        col_esq, col_dir = st.columns(2)

        with col_esq:
            st.plotly_chart(criar_waterfall(df), use_container_width=True)

        with col_dir:
            st.plotly_chart(criar_pareto(df), use_container_width=True)

        # Heatmap full width
        st.plotly_chart(criar_heatmap_sazonalidade(df), use_container_width=True)

    with tab_detalhes:
        # Variance Analysis
        st.markdown("### Variance Analysis (Realizado vs. Orçado)")
        df_var = criar_variance_analysis(df)

        st.dataframe(
            df_var.style.format({'Orçado': 'R$ {:,.0f}', 'Realizado': 'R$ {:,.0f}', 'Diferença': 'R$ {:,.0f}'})
            .set_properties(**{'background-color': '#F3F4F6', 'color': '#1F2937'}),
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")

        # Fluxo de Caixa Mensal
        st.markdown("### Fluxo de Caixa Mensal")
        tabela_mes = criar_tabela_por_mes(df)

        st.dataframe(
            tabela_mes.style.format('R$ {:,.0f}')
            .set_properties(**{'background-color': '#F3F4F6', 'color': '#1F2937'}),
            use_container_width=True
        )

else:
    st.warning("⚠️ Carregue dados para começar")

st.markdown("---")
