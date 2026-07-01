import streamlit as st
import pandas as pd

st.set_page_config(page_title="Fluxo de Caixa", layout="wide")

st.markdown("# Fluxo de Caixa - Ville de Provence")

with st.sidebar:
    st.markdown("## Upload de Dados")
    arquivo = st.file_uploader("Selecione CSV", type="csv")

if arquivo is not None:
    df = pd.read_csv(arquivo)
    st.success(f"Carregado: {len(df)} registros")
    st.dataframe(df)
else:
    st.info("Carregue um arquivo CSV")
