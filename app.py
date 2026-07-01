import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import json
import os

st.set_page_config(page_title="Fluxo de Caixa", layout="wide")
st.markdown("# Fluxo de Caixa - Ville de Provence")

# Arquivo de persistencia
ARQUIVO_PERSISTENCIA = "fluxo_caixa_data.json"

def carregar_dados_persistidos():
    """Carrega dados salvos localmente"""
    if os.path.exists(ARQUIVO_PERSISTENCIA):
        with open(ARQUIVO_PERSISTENCIA, 'r') as f:
            return json.load(f)
    return {}

def salvar_dados(dados):
    """Salva dados localmente"""
    with open(ARQUIVO_PERSISTENCIA, 'w') as f:
        json.dump(dados, f)

def obter_mes_atual():
    """Retorna ano-mes atual (ex: 2026-07)"""
    agora = datetime.now()
    return f"{agora.year}-{agora.month:02d}"

# Inicializar session state
if 'dados_fc' not in st.session_state:
    st.session_state.dados_fc = carregar_dados_persistidos()

mes_atual = obter_mes_atual()

with st.sidebar:
    st.markdown("## Upload CSV")
    arquivo = st.file_uploader("Selecione o CSV", type="csv")

    if arquivo is not None:
        df = pd.read_csv(arquivo)

        if 'DescricaoLinha' in df.columns and 'Valor' in df.columns:
            # Processar dados por linha
            for idx, row in df.iterrows():
                linha = row['DescricaoLinha']
                valor = float(row['Valor'])

                if linha not in st.session_state.dados_fc:
                    st.session_state.dados_fc[linha] = {}

                st.session_state.dados_fc[linha][mes_atual] = valor

            salvar_dados(st.session_state.dados_fc)
            st.success(f"Dados carregados para {mes_atual}")
        else:
            st.error("CSV deve ter colunas 'DescricaoLinha' e 'Valor'")

    st.markdown("---")
    st.markdown("## Entrada Manual")

    with st.form("form_entrada"):
        descricao = st.text_input("Descricao da Linha")
        mes_entrada = st.text_input("Mes (YYYY-MM)", value=mes_atual)
        valor_entrada = st.number_input("Valor (R$)", value=0.0)

        if st.form_submit_button("Adicionar"):
            if descricao and valor_entrada != 0:
                if descricao not in st.session_state.dados_fc:
                    st.session_state.dados_fc[descricao] = {}

                st.session_state.dados_fc[descricao][mes_entrada] = valor_entrada
                salvar_dados(st.session_state.dados_fc)
                st.success(f"Adicionado: {descricao} em {mes_entrada}")

# Processar dados para mostrar
if st.session_state.dados_fc:
    st.info(f"Mes Atual: {mes_atual}")

    # Metricas
    col1, col2, col3, col4 = st.columns(4)

    receitas = sum([v for k, v in st.session_state.dados_fc.items()
                   if v.get(mes_atual, 0) > 0 for v in [v.get(mes_atual, 0)]])
    despesas = sum([abs(v) for k, v in st.session_state.dados_fc.items()
                   if v.get(mes_atual, 0) < 0 for v in [v.get(mes_atual, 0)]])
    saldo = receitas - despesas

    col1.metric("Receitas", f"R$ {receitas:,.0f}")
    col2.metric("Despesas", f"R$ {despesas:,.0f}")
    col3.metric("Saldo", f"R$ {saldo:,.0f}")
    col4.metric("Status", "OK")

    # Tabs
    tab_dados, tab_graficos = st.tabs(["Planilha", "Graficos"])

    with tab_dados:
        st.markdown("### Tabela - Fluxo de Caixa por Mes")

        # Criar DataFrame pivotado
        dados_lista = []
        for linha, valores_mes in st.session_state.dados_fc.items():
            row = {"Linha": linha}
            row.update(valores_mes)
            dados_lista.append(row)

        if dados_lista:
            df_tabela = pd.DataFrame(dados_lista)

            # Ordena colunas por mes
            cols_mes = sorted([col for col in df_tabela.columns if col != "Linha" and len(col) == 7])
            df_tabela = df_tabela[["Linha"] + cols_mes]

            st.dataframe(df_tabela.set_index("Linha").style.format('R$ {:,.0f}'), use_container_width=True)

    with tab_graficos:
        st.markdown("### Evolucao de Custos - Tendencia por Mes")

        # Gráfico de linha
        meses_disponiveis = sorted(set(m for linha in st.session_state.dados_fc.values() for m in linha.keys()))

        if meses_disponiveis:
            fig_evolucao = go.Figure()

            # Top 5 linhas por valor no mes atual
            top_linhas = sorted([(k, v.get(mes_atual, 0)) for k, v in st.session_state.dados_fc.items()],
                               key=lambda x: abs(x[1]), reverse=True)[:5]

            for linha, _ in top_linhas:
                valores = [st.session_state.dados_fc[linha].get(mes, 0) for mes in meses_disponiveis]
                fig_evolucao.add_trace(go.Scatter(
                    x=meses_disponiveis,
                    y=valores,
                    mode='lines+markers',
                    name=linha[:20],
                    line=dict(width=2),
                ))

            fig_evolucao.update_layout(
                title='Custos Principais Mês a Mês',
                xaxis_title='Mes',
                yaxis_title='Valor (R$)',
                height=400,
                hovermode='x unified',
            )

            st.plotly_chart(fig_evolucao, use_container_width=True)

        st.markdown("### Pareto - Top Despesas do Mes Atual")

        despesas_linha = [(k, abs(v.get(mes_atual, 0))) for k, v in st.session_state.dados_fc.items()
                         if v.get(mes_atual, 0) < 0]
        despesas_linha = sorted(despesas_linha, key=lambda x: x[1], reverse=True)[:10]

        if despesas_linha:
            df_pareto = pd.DataFrame(despesas_linha, columns=["Linha", "Valor"])
            df_pareto["Pct"] = (df_pareto["Valor"] / df_pareto["Valor"].sum() * 100).round(1)

            fig_pareto = go.Figure()
            fig_pareto.add_trace(go.Bar(
                y=df_pareto["Linha"],
                x=df_pareto["Valor"],
                orientation='h',
                marker=dict(color='#6B7280'),
                text=df_pareto["Pct"].apply(lambda x: f"{x:.0f}%"),
                textposition='outside',
            ))

            fig_pareto.update_layout(height=400, margin=dict(l=150, r=0, t=0, b=0))
            st.plotly_chart(fig_pareto, use_container_width=True)

else:
    st.info("Carregue um CSV ou adicione dados manualmente")
