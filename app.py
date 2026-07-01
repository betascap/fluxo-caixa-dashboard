import streamlit as st
import pandas as pd

st.set_page_config(page_title="Fluxo de Caixa", layout="wide")
st.markdown("# Fluxo de Caixa - Ville de Provence")

with st.sidebar:
    st.markdown("## Upload")
    arquivo = st.file_uploader("CSV", type="csv")

if arquivo is not None:
    df = pd.read_csv(arquivo)

    st.success(f"OK - {len(df)} registros")

    col1, col2, col3, col4 = st.columns(4)

    receitas = df[df['Valor'] > 0]['Valor'].sum()
    despesas = abs(df[df['Valor'] < 0]['Valor'].sum())
    saldo = receitas - despesas

    col1.metric("Receitas", f"R$ {receitas:,.0f}")
    col2.metric("Despesas", f"R$ {despesas:,.0f}")
    col3.metric("Saldo", f"R$ {saldo:,.0f}")
    col4.metric("Runway", "N/A")

    tab1, tab2 = st.tabs(["Graficos", "Detalhes"])

    with tab1:
        st.markdown("### Dados")
        st.write("Graficos aqui")

    with tab2:
        st.markdown("### Tabela")
        st.dataframe(df.head(10))

else:
    st.info("Carregue um CSV")
