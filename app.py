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
    tab_dados, tab_graficos = st.tabs(["Planilha", "Graficos"])

    with tab_dados:
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

    with tab_graficos:
        # Evolucao de Custos no Tempo
        st.markdown("### Evolucao de Custos - Tendencia Mensal")

        df_evolucao = df[df['Valor'] < 0].copy()
        df_evolucao['Mes'] = df_evolucao['Data'].dt.to_period('M')
        df_evolucao['Valor_abs'] = abs(df_evolucao['Valor'])

        # Agregar por mes e categoria
        custos_por_mes = df_evolucao.groupby(['Mes', 'Categoria'])['Valor_abs'].sum().reset_index()
        custos_por_mes['Mes'] = custos_por_mes['Mes'].astype(str)

        # Pegar as top 5 categorias
        top_categorias = df_evolucao.groupby('Categoria')['Valor_abs'].sum().nlargest(5).index

        fig_evolucao = go.Figure()

        for cat in top_categorias:
            dados_cat = custos_por_mes[custos_por_mes['Categoria'] == cat]
            fig_evolucao.add_trace(go.Scatter(
                x=dados_cat['Mes'],
                y=dados_cat['Valor_abs'],
                mode='lines+markers',
                name=str(cat)[:20],
                line=dict(width=2),
            ))

        fig_evolucao.update_layout(
            title='Custos Principais Mês a Mês',
            xaxis_title='Mes',
            yaxis_title='Valor (R$)',
            height=400,
            margin=dict(l=0, r=0, t=30, b=0),
            hovermode='x unified',
        )

        st.plotly_chart(fig_evolucao, use_container_width=True)

        st.markdown("**Analise**: Veja qual categoria está crescendo, estagnando ou diminuindo. OBRA é normalmente a maior - se está crescendo muito, é sinal de alerta.")

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


else:
    st.info("Carregue um CSV")
