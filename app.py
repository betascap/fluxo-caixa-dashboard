"""
Dashboard Streamlit - Fluxo de Caixa Ville de Provence
Visualiza dados extraídos do Sienge em um painel interativo.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO
import os
from datetime import datetime

# Arquivo de persistência para entrada manual
ARQUIVO_MANUAL = "dados_manuais.csv"

# Configuração da página
st.set_page_config(
    page_title="Dashboard FC - Ville de Provence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado para tema coerente
st.markdown("""
<style>
    :root {
        --primary-color: #0066cc;
        --secondary-color: #27ae60;
        --danger-color: #e74c3c;
        --neutral-color: #95a5a6;
    }

    .stMetricValue {
        font-size: 2rem;
        font-weight: bold;
    }

    .metric-card {
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .positivo {
        color: #27ae60;
    }

    .negativo {
        color: #e74c3c;
    }

    h1, h2, h3 {
        color: #1a1a1a;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CONFIGURAÇÃO & DADOS
# ============================================================================

def carregar_csv(caminho):
    """Carrega o CSV de dados."""
    try:
        df = pd.read_csv(caminho)
        df['Data'] = pd.to_datetime(df['Data'])
        df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Erro ao carregar CSV: {e}")
        return None


def carregar_dados_manuais():
    """Carrega dados manuais persistidos em arquivo."""
    if os.path.exists(ARQUIVO_MANUAL):
        try:
            df = pd.read_csv(ARQUIVO_MANUAL)
            df['Data'] = pd.to_datetime(df['Data'])
            df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
            return df
        except:
            return pd.DataFrame()
    return pd.DataFrame()


def salvar_dados_manuais(df):
    """Salva dados manuais em arquivo (persiste)."""
    if df is not None and not df.empty:
        df.to_csv(ARQUIVO_MANUAL, index=False)


def adicionar_entrada_manual(data, descricao, valor, tipo):
    """Adiciona uma entrada manual e persiste."""
    df_manual = carregar_dados_manuais()

    nova_entrada = pd.DataFrame({
        'Data': [pd.Timestamp(data)],
        'CentroCusto': ['9999'],
        'Categoria': [tipo],
        'DescricaoLinha': [descricao],
        'Valor': [valor if tipo == 'Receita' else -abs(valor)]
    })

    df_manual = pd.concat([df_manual, nova_entrada], ignore_index=True)
    salvar_dados_manuais(df_manual)
    return df_manual


def processar_dados(df):
    """Processa dados para visualizações."""
    if df is None or df.empty:
        return None

    # Resumo por linha
    por_linha = df.groupby('DescricaoLinha').agg({
        'Valor': 'sum',
        'Categoria': 'first'
    }).reset_index().sort_values('Valor')

    # Resumo por categoria
    por_categoria = df.groupby('Categoria')['Valor'].sum().reset_index().sort_values('Valor')

    # Métricas gerais
    total_valor = df['Valor'].sum()
    total_despesas = abs(df[df['Valor'] < 0]['Valor'].sum())
    total_receitas = df[df['Valor'] > 0]['Valor'].sum()

    return {
        'por_linha': por_linha,
        'por_categoria': por_categoria,
        'total': total_valor,
        'despesas': total_despesas,
        'receitas': total_receitas,
        'saldo': total_receitas - total_despesas,
    }


def criar_tabela_pivotada(df):
    """Cria tabela pivotada: Linhas = Categorias, Colunas = Meses."""
    if df is None or df.empty:
        return None

    df_piv = df.copy()
    df_piv['Mes'] = df_piv['Data'].dt.to_period('M')

    # Pivotar
    tabela = df_piv.pivot_table(
        index='DescricaoLinha',
        columns='Mes',
        values='Valor',
        aggfunc='sum',
        fill_value=0
    )

    # Adicionar coluna TOTAL
    tabela['TOTAL'] = tabela.sum(axis=1)
    tabela = tabela.sort_values('TOTAL')

    return tabela


def exportar_excel(df, nome_arquivo="fluxo_caixa.xlsx"):
    """Exporta dados em Excel com 3 abas."""
    output = BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Aba 1: Tabela Pivotada (Mês × Categoria)
        tabela_piv = criar_tabela_pivotada(df)
        if tabela_piv is not None:
            tabela_piv_reset = tabela_piv.reset_index()
            tabela_piv_reset.to_excel(writer, sheet_name='FC por Mês', index=False)

        # Aba 2: Resumo por Linha
        df_export = df.groupby('DescricaoLinha').agg({
            'Valor': 'sum',
            'Categoria': 'first'
        }).reset_index()
        df_export = df_export.sort_values('Valor')
        df_export.columns = ['Descrição', 'Valor', 'Categoria']
        df_export.to_excel(writer, sheet_name='Fluxo de Caixa', index=False)

        # Aba 3: Dados brutos
        df_bruto = df[['Data', 'CentroCusto', 'Categoria', 'DescricaoLinha', 'Valor']].copy()
        df_bruto.columns = ['Data', 'Centro de Custo', 'Categoria', 'Descrição', 'Valor']
        df_bruto.to_excel(writer, sheet_name='Dados Brutos', index=False)

        # Formatação básica
        for ws in writer.book.worksheets:
            for column in ws.columns:
                max_length = 0
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = (max_length + 2)
                ws.column_dimensions[column[0].column_letter].width = adjusted_width

    output.seek(0)
    return output


# ============================================================================
# LAYOUT & INTERFACE
# ============================================================================

# Header
col1, col2 = st.columns([0.1, 0.9])
with col1:
    st.markdown("## 📊")
with col2:
    st.markdown("## Fluxo de Caixa - Ville de Provence")

st.markdown("---")

# ============================================================================
# SIDEBAR: Upload e Filtros
# ============================================================================

with st.sidebar:
    st.markdown("## ⚙️ Configurações")

    # ========== ENTRADA MANUAL ==========
    st.markdown("### ➕ Entrada Manual de Dados")

    with st.form("form_entrada"):
        col1, col2 = st.columns(2)
        with col1:
            data_entrada = st.date_input("Data", value=pd.Timestamp.now())
        with col2:
            tipo_entrada = st.selectbox("Tipo", ["Despesa", "Receita", "Ajuste"])

        descricao_entrada = st.text_input("Descrição")
        valor_entrada = st.number_input("Valor (R$)", value=0.0, step=100.0)

        submitted = st.form_submit_button("➕ Adicionar")

        if submitted and descricao_entrada and valor_entrada != 0:
            adicionar_entrada_manual(data_entrada, descricao_entrada, valor_entrada, tipo_entrada)
            st.success(f"✅ {descricao_entrada} adicionado e salvo!")
            st.rerun()

    # Mostrar entradas manuais existentes
    df_manual_atual = carregar_dados_manuais()
    if not df_manual_atual.empty:
        st.markdown("### 📝 Entradas Manuais Salvas")

        for idx, row in df_manual_atual.iterrows():
            col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 1])
            with col1:
                st.caption(row['Data'].strftime('%d/%m/%Y'))
            with col2:
                st.caption(row['DescricaoLinha'])
            with col3:
                st.caption(f"R$ {row['Valor']:,.2f}")
            with col4:
                st.caption(row['Categoria'])
            with col5:
                if st.button("🗑️", key=f"del_{idx}"):
                    df_manual_atual = df_manual_atual.drop(idx)
                    salvar_dados_manuais(df_manual_atual)
                    st.success("Deletado!")
                    st.rerun()

    st.markdown("---")

    # Selecionar arquivo
    st.markdown("### 📁 Dados")

    # Verificar se existe fc_dados.csv na pasta output
    csv_padrao = os.path.join(os.path.dirname(__file__), "output", "fc_dados.csv")

    if os.path.exists(csv_padrao):
        usar_padrao = st.checkbox("Usar arquivo padrão (output/fc_dados.csv)", value=True)
        if usar_padrao:
            caminho_csv = csv_padrao
        else:
            caminho_csv = st.file_uploader("Ou selecione um CSV", type="csv")
    else:
        caminho_csv = st.file_uploader("Selecione o arquivo CSV", type="csv")

    if caminho_csv is not None:
        if isinstance(caminho_csv, str):
            df = carregar_csv(caminho_csv)
        else:
            df = carregar_csv(caminho_csv.name)

        if df is not None:
            st.success(f"✅ {len(df)} registros carregados")

            # Info geral
            st.markdown("### 📅 Período")
            if not df.empty:
                data_min = df['Data'].min()
                data_max = df['Data'].max()
                st.caption(f"{data_min.strftime('%B/%Y')} a {data_max.strftime('%B/%Y')}")

            # Filtros
            st.markdown("### 🔍 Filtros")

            categorias = sorted(df['Categoria'].unique())
            categoria_selecionada = st.multiselect(
                "Categorias",
                categorias,
                default=categorias,
                key="cat_filter"
            )

            df_filtrado = df[df['Categoria'].isin(categoria_selecionada)] if categoria_selecionada else df

            # Consolidar com dados manuais persistidos
            df_manual = carregar_dados_manuais()
            if not df_manual.empty:
                df_filtrado = pd.concat([df_filtrado, df_manual], ignore_index=True)
                n_manual = len(df_manual)
                st.info(f"📝 {n_manual} entrada(s) manual(is) consolidada(s)")

            # Processar dados
            dados = processar_dados(df_filtrado)

        else:
            df = None
            df_filtrado = None
            dados = None
    else:
        st.info("👆 Carregue um arquivo CSV para começar")
        df = None
        df_filtrado = None
        dados = None


# ============================================================================
# CONTEÚDO PRINCIPAL
# ============================================================================

if dados is not None:
    # Tabs principais
    tab1, tab2, tab3 = st.tabs(["📋 Fluxo de Caixa", "📈 Análise", "📅 FC por Mês"])

    # ====================================================================
    # ABA 1: FLUXO DE CAIXA
    # ====================================================================
    with tab1:
        st.markdown("### Resumo por Linha de Despesa")

        # Tabela de FC
        df_tabela = dados['por_linha'].copy()
        df_tabela['Valor'] = df_tabela['Valor'].apply(lambda x: f"R$ {x:,.2f}")
        df_tabela.columns = ['Descrição', 'Valor', 'Categoria']

        # Formatação com cores
        def colorir_valor(val):
            if 'R$' in val:
                try:
                    num = float(val.replace('R$', '').replace('.', '').replace(',', '.'))
                    if num < 0:
                        return 'color: red'
                    else:
                        return 'color: green'
                except:
                    return ''
            return ''

        st.dataframe(
            df_tabela,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Valor": st.column_config.TextColumn(width="medium"),
                "Descrição": st.column_config.TextColumn(width="large"),
                "Categoria": st.column_config.TextColumn(width="medium"),
            }
        )

        # Download
        st.markdown("---")
        col1, col2 = st.columns([0.5, 0.5])

        with col1:
            excel_file = exportar_excel(df_filtrado)
            st.download_button(
                label="📥 Baixar em Excel",
                data=excel_file,
                file_name=f"fluxo_caixa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        with col2:
            st.markdown("")  # Espaço

    # ====================================================================
    # ABA 2: ANÁLISE
    # ====================================================================
    with tab2:
        # KPI Cards
        st.markdown("### 🎯 Resumo Executivo")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Total",
                f"R$ {dados['total']:,.2f}",
                delta=None,
                delta_color="off"
            )

        with col2:
            st.metric(
                "Receitas",
                f"R$ {dados['receitas']:,.2f}",
                delta=None,
                delta_color="off"
            )

        with col3:
            st.metric(
                "Despesas",
                f"R$ {dados['despesas']:,.2f}",
                delta=None,
                delta_color="off"
            )

        with col4:
            cor_saldo = "green" if dados['saldo'] >= 0 else "red"
            st.metric(
                "Saldo",
                f"R$ {dados['saldo']:,.2f}",
                delta=None,
                delta_color="off"
            )

        st.markdown("---")

        # Gráficos
        st.markdown("### 📊 Visualizações")

        col1, col2 = st.columns(2)

        # Gráfico 1: Pizza por Categoria
        with col1:
            st.markdown("#### Distribuição por Categoria")

            df_cat = dados['por_categoria'].copy()
            df_cat['Valor_abs'] = df_cat['Valor'].abs()

            fig_pizza = px.pie(
                df_cat,
                values='Valor_abs',
                names='Categoria',
                color_discrete_sequence=px.colors.qualitative.Set3,
                hole=0.4
            )
            fig_pizza.update_traces(textposition='inside', textinfo='label+percent')
            fig_pizza.update_layout(
                height=400,
                showlegend=True,
                margin=dict(t=0, b=0, l=0, r=0)
            )
            st.plotly_chart(fig_pizza, use_container_width=True)

        # Gráfico 2: Top 5 Despesas
        with col2:
            st.markdown("#### Top 5 Maiores Despesas")

            df_top = dados['por_linha'].nsmallest(5, 'Valor').copy()
            df_top['Valor_abs'] = df_top['Valor'].abs()

            fig_barras = px.bar(
                df_top,
                y='DescricaoLinha',
                x='Valor_abs',
                orientation='h',
                color='Valor_abs',
                color_continuous_scale='Reds',
                labels={'DescricaoLinha': '', 'Valor_abs': 'Valor (R$)'}
            )
            fig_barras.update_layout(
                height=400,
                showlegend=False,
                margin=dict(t=0, b=0, l=200, r=0)
            )
            st.plotly_chart(fig_barras, use_container_width=True)

        # Gráfico 3: Tabela de Categorias
        st.markdown("#### Resumo por Categoria")

        df_cat_resumo = dados['por_categoria'].copy()
        df_cat_resumo['Valor'] = df_cat_resumo['Valor'].apply(lambda x: f"R$ {x:,.2f}")
        df_cat_resumo.columns = ['Categoria', 'Valor']

        st.dataframe(
            df_cat_resumo,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Categoria": st.column_config.TextColumn(width="large"),
                "Valor": st.column_config.TextColumn(width="medium"),
            }
        )

    # ====================================================================
    # ABA 3: FC POR MÊS (PIVOTADA)
    # ====================================================================
    with tab3:
        st.markdown("### Fluxo de Caixa Mensal (Categoria × Mês)")

        tabela_piv = criar_tabela_pivotada(df_filtrado)

        if tabela_piv is not None:
            # Converter para display format
            df_display = tabela_piv.reset_index()

            # Formatar valores como moeda
            for col in df_display.columns[1:]:
                df_display[col] = df_display[col].apply(lambda x: f"R$ {x:,.2f}" if pd.notna(x) else "R$ 0,00")

            st.dataframe(
                df_display,
                use_container_width=True,
                hide_index=True
            )

            st.markdown("---")

            # Download da tabela pivotada
            col1, col2 = st.columns([0.5, 0.5])
            with col1:
                excel_file = exportar_excel(df_filtrado)
                st.download_button(
                    label="📥 Baixar Completo em Excel",
                    data=excel_file,
                    file_name=f"fluxo_caixa_completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        else:
            st.warning("Não há dados para exibir a tabela pivotada.")

else:
    st.warning("⚠️ Nenhum arquivo carregado. Carregue um CSV na barra lateral para começar.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #95a5a6; font-size: 0.85rem;'>
    Dashboard FC v1.0 | Ville de Provence | Dados atualizados automaticamente
    </div>
    """,
    unsafe_allow_html=True
)
