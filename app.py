import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Fluxo de Caixa", layout="wide")
st.markdown("# Fluxo de Caixa - Ville de Provence")

with st.sidebar:
    st.markdown("## Upload")
    arquivo = st.file_uploader("CSV", type="csv")

if arquivo is not None:
    df = pd.read_csv(arquivo)
    df['Data'] = pd.to_datetime(df['Data'])

    st.success(f"OK - {len(df)} registros")

    # Metricas
    col1, col2, col3, col4 = st.columns(4)

    receitas = df[df['Valor'] > 0]['Valor'].sum()
    despesas = abs(df[df['Valor'] < 0]['Valor'].sum())
    saldo = receitas - despesas
    dias = (df['Data'].max() - df['Data'].min()).days + 1
    burn = abs(saldo) / max(dias, 1) * 30
    runway = saldo / max(burn, 0.01) if burn > 0 else 999

    col1.metric("Receitas", f"R$ {receitas:,.0f}")
    col2.metric("Despesas", f"R$ {despesas:,.0f}")
    col3.metric("Saldo", f"R$ {saldo:,.0f}")
    col4.metric("Runway", f"{runway:.1f} meses")

    # Tabs
    tab1, tab2 = st.tabs(["Graficos", "Detalhes"])

    with tab1:
        # Waterfall
        st.markdown("### Waterfall - Fluxo de Caixa")

        receitas_val = df[df['Valor'] > 0]['Valor'].sum()
        despesas_cat = df[df['Valor'] < 0].groupby('Categoria')['Valor'].sum().sort_values()

        nomes = ['Inicial']
        valores = [0]

        nomes.append('Receitas')
        valores.append(receitas_val)

        for cat, val in despesas_cat.items():
            nomes.append(str(cat)[:20])
            valores.append(val)

        nomes.append('Final')
        valores.append(0)

        fig_waterfall = go.Figure(go.Waterfall(
            x=nomes,
            y=valores,
            increasing=dict(marker=dict(color='#6B7280')),
            decreasing=dict(marker=dict(color='#DC2626')),
        ))

        fig_waterfall.update_layout(height=400, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig_waterfall, use_container_width=True)

        # Pareto
        st.markdown("### Pareto - Top Despesas")

        despesas_df = df[df['Valor'] < 0].copy()
        despesas_df['Valor_abs'] = abs(despesas_df['Valor'])

        top10 = despesas_df.groupby('DescricaoLinha')['Valor_abs'].sum().nlargest(10).reset_index()
        top10 = top10.sort_values('Valor_abs', ascending=True)
        top10['Pct'] = (top10['Valor_abs'] / top10['Valor_abs'].sum() * 100).round(1)

        fig_pareto = go.Figure()

        fig_pareto.add_trace(go.Bar(
            y=top10['DescricaoLinha'],
            x=top10['Valor_abs'],
            orientation='h',
            marker=dict(color='#6B7280'),
            text=top10['Pct'].apply(lambda x: f"{x:.0f}%"),
            textposition='outside',
        ))

        fig_pareto.update_layout(height=400, margin=dict(l=150, r=0, t=0, b=0))
        st.plotly_chart(fig_pareto, use_container_width=True)

        # Heatmap
        st.markdown("### Heatmap - Sazonalidade")

        df_piv = df.copy()
        df_piv['Mes'] = df_piv['Data'].dt.to_period('M')

        tabela_heat = df_piv.pivot_table(
            index='Categoria',
            columns='Mes',
            values='Valor',
            aggfunc='sum',
            fill_value=0
        )

        fig_heat = go.Figure(data=go.Heatmap(
            z=tabela_heat.values,
            x=[str(c) for c in tabela_heat.columns],
            y=tabela_heat.index,
            colorscale='Greys',
        ))

        fig_heat.update_layout(height=300, margin=dict(l=150, r=0, t=0, b=0))
        st.plotly_chart(fig_heat, use_container_width=True)

    with tab2:
        st.markdown("### Tabela - Dados Brutos")

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

else:
    st.info("Carregue um CSV")
