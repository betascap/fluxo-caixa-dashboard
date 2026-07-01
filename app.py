"""
Dashboard Fluxo de Caixa - Ville de Provence
Versão simplificada
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Fluxo de Caixa", layout="wide")

st.markdown("# 💰 Fluxo de Caixa - Ville de Provence")

with st.sidebar:
    st.markdown("## Upload de Dados")
    arquivo = st.file_uploader("Carregue o CSV", type="csv")

if arquivo is not None:
    try:
        df = pd.read_csv(arquivo)
        df['Data'] = pd.to_datetime(df['Data'])

        st.success(f"✅ {len(df)} registros carregados")

        # Métricas
        col1, col2, col3, col4 = st.columns(4)

        receitas = df[df['Valor'] > 0]['Valor'].sum()
        despesas = abs(df[df['Valor'] < 0]['Valor'].sum())
        saldo = receitas - despesas

        with col1:
            st.metric("Receitas", f"R$ {receitas:,.0f}")
        with col2:
            st.metric("Despesas", f"R$ {despesas:,.0f}")
        with col3:
            st.metric("Saldo", f"R$ {saldo:,.0f}")
        with col4:
            dias = (df['Data'].max() - df['Data'].min()).days + 1
            burn = abs(saldo) / max(dias, 1) * 30
            runway = saldo / max(burn, 0.01) if burn > 0 else 999
            st.metric("Runway", f"{runway:.1f} meses")

        # Abas
        tab1, tab2 = st.tabs(["📊 Gráficos", "📋 Detalhes"])

        with tab1:
            st.markdown("### Waterfall - Fluxo de Caixa")

            receitas_val = df[df['Valor'] > 0]['Valor'].sum()
            despesas_cat = df[df['Valor'] < 0].groupby('Categoria')['Valor'].sum().sort_values()

            nomes = ['Inicial']
            valores = [0]

            nomes.append(f'Receitas: {receitas_val:,.0f}')
            valores.append(receitas_val)

            for cat, val in despesas_cat.items():
                nomes.append(f'{cat}: {val:,.0f}')
                valores.append(val)

            nomes.append('Saldo Final')
            valores.append(0)

            fig = go.Figure(go.Waterfall(
                x=nomes,
                y=valores,
                increasing=dict(marker=dict(color='#6B7280')),
                decreasing=dict(marker=dict(color='#DC2626')),
            ))

            fig.update_layout(height=400, margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.markdown("### Dados por Mês")

            df_piv = df.copy()
            df_piv['Mes'] = df_piv['Data'].dt.to_period('M')

            tabela = df_piv.pivot_table(
                index='DescricaoLinha',
                columns='Mes',
                values='Valor',
                aggfunc='sum',
                fill_value=0
            )

            tabela['TOTAL'] = tabela.sum(axis=1)

            st.dataframe(tabela.style.format('R$ {:,.0f}'), use_container_width=True)

    except Exception as e:
        st.error(f"Erro: {str(e)}")

else:
    st.info("👆 Carregue um arquivo CSV para começar")
