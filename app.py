import streamlit as st

st.set_page_config(page_title="FC", layout="wide")
st.markdown("# 💰 Fluxo de Caixa")

with st.sidebar:
    arquivo = st.file_uploader("CSV", type="csv")

if arquivo:
    import pandas as pd
    df = pd.read_csv(arquivo)
    st.write(f"✅ {len(df)} registros")
    st.dataframe(df)
else:
    st.info("Carregue um CSV")
