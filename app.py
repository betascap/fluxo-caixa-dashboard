import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import json
import os
import re
import pdfplumber

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

def detectar_colunas_mes(colunas):
    """Detecta colunas que representam meses no formato YYYY-MM ou similar"""
    meses_detectados = []
    padrao = r'^\d{4}-\d{2}$'

    for col in colunas:
        col_str = str(col).strip()
        if re.match(padrao, col_str):
            meses_detectados.append(col_str)

    return sorted(meses_detectados)

def processar_planilha_historica(df):
    """Processa planilha histórica com estrutura: Linha | 2026-01 | 2026-02 | ..."""
    # Primeira coluna é identificador da linha
    primeira_col = df.columns[0]
    df = df.rename(columns={primeira_col: "Linha"})

    # Detecta colunas de mês
    meses = detectar_colunas_mes(df.columns)

    if not meses:
        return None, "Nenhuma coluna de mês detectada. Use formato YYYY-MM"

    # Filtra apenas colunas de mês + Linha
    df_filtrado = df[["Linha"] + meses].copy()

    # Remove linhas vazias
    df_filtrado = df_filtrado.dropna(subset=["Linha"])
    df_filtrado["Linha"] = df_filtrado["Linha"].astype(str).str.strip()

    # Converte valores para float
    for mes in meses:
        df_filtrado[mes] = pd.to_numeric(df_filtrado[mes], errors='coerce').fillna(0)

    return df_filtrado, None

def processar_pdf(arquivo_pdf):
    """Extrai tabela de PDF e converte em DataFrame"""
    try:
        with pdfplumber.open(arquivo_pdf) as pdf:
            primeira_pagina = pdf.pages[0]
            tabela = primeira_pagina.extract_table()

            if tabela:
                # Converte para DataFrame
                df = pd.DataFrame(tabela[1:], columns=tabela[0])
                return df, None
            else:
                return None, "Nenhuma tabela encontrada no PDF"
    except Exception as e:
        return None, f"Erro ao ler PDF: {str(e)}"

def mapear_categoria(descricao):
    """Mapeia descrição do credor para categoria padrão"""
    descricao_lower = descricao.lower()

    # Dicionário de mapeamentos (palavras-chave → categoria)
    mapeamentos = {
        "Comissões S/ Venda (Equipe Interna)": [
            "comiss", "vendedor", "corretagem", "intermediacao", "venda"
        ],
        "Outras Despesas (adm)": [
            "tarifa", "banco", "ted", "pix", "transferencia", "taxa",
            "manutencao c/c", "juros", "iof"
        ],
        "Marketing": [
            "marketing", "publicidade", "anuncio", "amplifique", "vegas card",
            "outdoor", "propaganda"
        ],
        "Stand de Venda - Manutenção": [
            "stand", "venda", "bolo", "bolacha", "alimentacao", "gas",
            "colorpress", "bebida", "alimento", "papelaria", "nipon"
        ],
        "Incorporação": [
            "incorporacao", "tabeliao", "registro", "protesto", "escritura",
            "cartorio"
        ],
        "OBRA - (revisão ABRIL/26)": [
            "obra", "concreto", "construcao", "concrebase", "material",
            "eletrica", "piratininga", "mexichem", "limpeza obra"
        ],
        "IPTU Estoque": [
            "iptu", "imposto predial", "imovel estoque"
        ],
        "Impostos": [
            "imposto", "irpj", "pis", "cofins", "icms", "pje",
            "receita federal", "ministerio", "governo"
        ],
        "ITBI": [
            "itbi", "imposto transmissao", "registro imobiliario"
        ],
        "Aluguel": [
            "aluguel", "alugel", "locacao", "sala", "escritorio"
        ],
        "Comissões": [
            "comiss", "corretagem", "intermediacao"
        ],
        "Energia": [
            "energia", "luz", "eletricidade", "claro", "piratininga",
            "cpfl", "eletropaulo"
        ],
        "Agua e Esgoto": [
            "agua", "esgoto", "saae", "sabesp", "saneamento", "hidraulico"
        ],
        "Telefone": [
            "telefone", "fone", "voi", "claro", "oi", "tim", "vivo",
            "internet", "telefonica"
        ],
        "Manutencao": [
            "manutencao", "manutencão", "reparo", "conserto", "servico",
            "urbano desenvolvimento", "instalacao", "limpeza"
        ],
        "Limpeza": [
            "limpeza", "lixo", "vassoura", "desinfeccao", "higiene"
        ],
        "Seguranca": [
            "seguranca", "segurança", "vigilancia", "vigia", "monitoramento",
            "arganet"
        ],
    }

    # Tenta encontrar match
    for categoria, palavras_chave in mapeamentos.items():
        for palavra in palavras_chave:
            if palavra in descricao_lower:
                return categoria

    # Se não encontrar, retorna a descrição original
    return descricao

def extrair_contas_pagas(arquivo_pdf):
    """Extrai contas pagas de PDF Sienge e retorna DataFrame com Categoria e Valor"""
    try:
        dados = []

        with pdfplumber.open(arquivo_pdf) as pdf:
            if not pdf.pages:
                return None, "PDF vazio ou corrupto"

            for page_num, page in enumerate(pdf.pages):
                try:
                    tables = page.extract_tables()
                    if not tables:
                        continue

                    for table in tables:
                        if not table or len(table) < 3:
                            continue

                        # Procura o índice da coluna "Líquido"
                        liquido_idx = -1
                        for col_idx, header_cell in enumerate(table[1]):
                            if header_cell and "Líquido" in str(header_cell):
                                liquido_idx = col_idx
                                break

                        if liquido_idx < 0:
                            continue

                        # Processa linhas de dados (começa em linha 2)
                        for row_idx in range(2, len(table)):
                            try:
                                row = table[row_idx]
                                if not row or len(row) == 0:
                                    continue

                                credor = str(row[0]).strip() if row[0] else ""

                                # Validações
                                if not credor or len(credor) < 2:
                                    continue
                                if "Obs " in credor or "Total" in credor or "Subtotal" in credor:
                                    continue

                                # Limpa quebras de linha e espaços
                                credor = " ".join(credor.split())

                                # Extrai valor
                                if liquido_idx < len(row) and row[liquido_idx]:
                                    valor_str = str(row[liquido_idx]).replace("T", "").replace(",", ".").strip()
                                    try:
                                        valor = float(valor_str)
                                        if valor != 0:  # Só adiciona valores não-zero
                                            valor = -abs(valor)
                                            categoria = mapear_categoria(credor)

                                            dados.append({
                                                "Linha": categoria,
                                                "Valor": valor
                                            })
                                    except ValueError:
                                        pass

                            except Exception as e:
                                continue

                except Exception as e:
                    continue

        if not dados:
            return None, "Nenhum dado encontrado no PDF"

        df = pd.DataFrame(dados)
        if len(df) > 0:
            # Agrupa por categoria (soma valores iguais)
            df_agrupado = df.groupby("Linha", as_index=False)["Valor"].sum()
            return df_agrupado, None
        else:
            return None, "Erro ao processar dados extraídos"

    except Exception as e:
        return None, f"Erro ao ler PDF: {str(e)}"

# Inicializar session state
if 'dados_fc' not in st.session_state:
    st.session_state.dados_fc = carregar_dados_persistidos()

mes_atual = obter_mes_atual()

with st.sidebar:
    st.markdown("## Upload de Dados")

    tab_upload_atual, tab_upload_historico = st.tabs(["Mes Atual", "Historico"])

    with tab_upload_atual:
        st.markdown("### Carregar Dados do Mes Atual")

        tipo_arquivo = st.radio("Tipo de arquivo:", ["CSV Sienge", "PDF Contas Pagas"], horizontal=True, key="tipo_upload")

        if tipo_arquivo == "CSV Sienge":
            arquivo = st.file_uploader("Selecione o CSV", type="csv", key="upload_csv_atual")

            if arquivo is not None:
                df = pd.read_csv(arquivo)

                if 'DescricaoLinha' in df.columns and 'Valor' in df.columns:
                    # Processar dados por linha
                    for idx, row in df.iterrows():
                        linha = row['DescricaoLinha']
                        valor = float(row['Valor'])

                        if linha not in st.session_state.dados_fc:
                            st.session_state.dados_fc[linha] = {}

                        # Acumula valor (permite múltiplas fontes)
                        if mes_atual not in st.session_state.dados_fc[linha]:
                            st.session_state.dados_fc[linha][mes_atual] = 0

                        st.session_state.dados_fc[linha][mes_atual] += valor

                    salvar_dados(st.session_state.dados_fc)
                    st.success(f"Dados carregados para {mes_atual}")
                else:
                    st.error("CSV deve ter colunas 'DescricaoLinha' e 'Valor'")

        else:  # PDF Contas Pagas
            arquivo_pdf = st.file_uploader("Selecione o PDF de Contas Pagas", type="pdf", key="upload_pdf_contas")

            if arquivo_pdf is not None:
                try:
                    with st.spinner("Extraindo dados do PDF..."):
                        df_extraido, erro = extrair_contas_pagas(arquivo_pdf)

                    if erro:
                        st.error(f"❌ {erro}")
                    elif df_extraido is None or len(df_extraido) == 0:
                        st.error("❌ Nenhum dado foi extraído do PDF")
                    else:
                        st.success(f"✅ {len(df_extraido)} categorias encontradas!")

                        with st.expander("Preview dos Dados Extraídos"):
                            st.dataframe(df_extraido.style.format({'Valor': 'R$ {:,.2f}'}), use_container_width=True)

                        if st.button("Importar Contas Pagas para " + mes_atual, key="btn_importar_contas"):
                            for idx, row in df_extraido.iterrows():
                                linha = row['Linha']
                                valor = float(row['Valor'])

                                if linha not in st.session_state.dados_fc:
                                    st.session_state.dados_fc[linha] = {}

                                # Acumula valor (permite múltiplas fontes)
                                if mes_atual not in st.session_state.dados_fc[linha]:
                                    st.session_state.dados_fc[linha][mes_atual] = 0

                                st.session_state.dados_fc[linha][mes_atual] += valor

                            salvar_dados(st.session_state.dados_fc)
                            st.success(f"✅ Contas pagas importadas para {mes_atual}!")
                            st.rerun()

                except Exception as e:
                    st.error(f"❌ Erro ao processar PDF: {str(e)}")

    with tab_upload_historico:
        st.markdown("### Carregar Dados de Mes Anterior")

        # Seletor de mês primeiro
        col_mes, col_ano = st.columns(2)
        with col_mes:
            mes_historico = st.selectbox("Mes", range(1, 13), format_func=lambda x: f"{x:02d}", key="mes_historico")
        with col_ano:
            ano_historico = st.number_input("Ano", value=2026, min_value=2020, max_value=2030, key="ano_historico")

        mes_selecionado = f"{ano_historico}-{mes_historico:02d}"
        st.info(f"Dados serão importados para: **{mes_selecionado}**")

        st.markdown("---")

        tipo_arquivo_hist = st.radio("Tipo de arquivo:", ["CSV/Excel", "PDF Contas Pagas"], horizontal=True, key="tipo_upload_hist")

        if tipo_arquivo_hist == "CSV/Excel":
            arquivo_historico = st.file_uploader(
                "CSV ou Excel com os dados do mes",
                type=["csv", "xlsx", "xls"],
                key="upload_historico_csv"
            )

            if arquivo_historico is not None:
                try:
                    # Detecta tipo de arquivo
                    if arquivo_historico.name.endswith('.csv'):
                        df_hist = pd.read_csv(arquivo_historico)
                    else:
                        df_hist = pd.read_excel(arquivo_historico)

                    # Pega primeira coluna (categoria) e segunda coluna (valor)
                    primeira_col = df_hist.columns[0]
                    segunda_col = df_hist.columns[1] if len(df_hist.columns) > 1 else None

                    if segunda_col:
                        df_hist = df_hist[[primeira_col, segunda_col]].rename(
                            columns={primeira_col: "Linha", segunda_col: "Valor"}
                        )
                        df_hist["Valor"] = pd.to_numeric(df_hist["Valor"], errors='coerce')
                        df_hist = df_hist.dropna(subset=["Valor"])

                        with st.expander("Preview dos Dados"):
                            st.dataframe(df_hist.style.format({'Valor': 'R$ {:,.0f}'}), use_container_width=True)

                        if st.button("Importar para " + mes_selecionado, key="btn_importar_mes_csv"):
                            for idx, row in df_hist.iterrows():
                                linha = str(row['Linha']).strip()
                                valor = float(row['Valor'])

                                if linha not in st.session_state.dados_fc:
                                    st.session_state.dados_fc[linha] = {}

                                # Acumula valor (permite múltiplas fontes)
                                if mes_selecionado not in st.session_state.dados_fc[linha]:
                                    st.session_state.dados_fc[linha][mes_selecionado] = 0

                                st.session_state.dados_fc[linha][mes_selecionado] += valor

                            salvar_dados(st.session_state.dados_fc)
                            st.success(f"Dados importados para {mes_selecionado}!")
                            st.rerun()
                    else:
                        st.error("Arquivo precisa ter pelo menos 2 colunas")

                except Exception as e:
                    st.error(f"Erro ao ler arquivo: {str(e)}")

        else:  # PDF Contas Pagas
            arquivo_pdf_hist = st.file_uploader(
                "PDF de Contas Pagas do mês",
                type="pdf",
                key="upload_historico_pdf"
            )

            if arquivo_pdf_hist is not None:
                try:
                    with st.spinner("Extraindo dados do PDF..."):
                        df_extraido_hist, erro_hist = extrair_contas_pagas(arquivo_pdf_hist)

                    if erro_hist:
                        st.error(f"❌ {erro_hist}")
                    elif df_extraido_hist is None or len(df_extraido_hist) == 0:
                        st.error("❌ Nenhum dado foi extraído do PDF")
                    else:
                        st.success(f"✅ {len(df_extraido_hist)} categorias encontradas!")

                        with st.expander("Preview dos Dados Extraídos"):
                            st.dataframe(df_extraido_hist.style.format({'Valor': 'R$ {:,.2f}'}), use_container_width=True)

                        if st.button("Importar Contas Pagas para " + mes_selecionado, key="btn_importar_contas_hist"):
                            for idx, row in df_extraido_hist.iterrows():
                                linha = row['Linha']
                                valor = float(row['Valor'])

                                if linha not in st.session_state.dados_fc:
                                    st.session_state.dados_fc[linha] = {}

                                # Acumula valor (permite múltiplas fontes)
                                if mes_selecionado not in st.session_state.dados_fc[linha]:
                                    st.session_state.dados_fc[linha][mes_selecionado] = 0

                                st.session_state.dados_fc[linha][mes_selecionado] += valor

                            salvar_dados(st.session_state.dados_fc)
                            st.success(f"✅ Contas pagas importadas para {mes_selecionado}!")
                            st.rerun()

                except Exception as e:
                    st.error(f"❌ Erro ao processar PDF: {str(e)}")

    st.markdown("---")
    st.markdown("## Entrada de Dados")

    tab_nova, tab_historica = st.tabs(["Nova Entrada", "Dados Historicos"])

    with tab_nova:
        with st.form("form_entrada_nova"):
            descricao = st.text_input("Descricao da Linha")
            mes_entrada = st.text_input("Mes (YYYY-MM)", value=mes_atual)
            valor_entrada = st.number_input("Valor (R$)", value=0.0)
            orcamento = st.number_input("Orcamento Mensal (R$)", value=0.0)

            if st.form_submit_button("Adicionar"):
                if descricao and valor_entrada != 0:
                    if descricao not in st.session_state.dados_fc:
                        st.session_state.dados_fc[descricao] = {}
                    if "orcamento" not in st.session_state.dados_fc:
                        st.session_state.dados_fc["orcamento"] = {}

                    st.session_state.dados_fc[descricao][mes_entrada] = valor_entrada

                    if orcamento > 0:
                        if descricao not in st.session_state.dados_fc["orcamento"]:
                            st.session_state.dados_fc["orcamento"][descricao] = {}
                        st.session_state.dados_fc["orcamento"][descricao][mes_entrada] = orcamento

                    salvar_dados(st.session_state.dados_fc)
                    st.success(f"Adicionado: {descricao} em {mes_entrada}")
                else:
                    st.error("Preencha descricao e valor")

    with tab_historica:
        st.markdown("### Editar Dados Historicos")

        if st.session_state.dados_fc:
            linhas_lista = sorted([k for k in st.session_state.dados_fc.keys() if k != "orcamento"])

            coluna_linha, coluna_mes, coluna_valor = st.columns([2, 1, 1])

            with coluna_linha:
                linha_selecionada = st.selectbox("Selecione a Linha", linhas_lista, key="linha_edit")

            if linha_selecionada:
                meses_linha = sorted(st.session_state.dados_fc[linha_selecionada].keys())

                with coluna_mes:
                    mes_selecionado = st.selectbox("Mes", meses_linha, key="mes_edit")

                with coluna_valor:
                    # Verifica se o valor existe antes de acessar
                    if mes_selecionado in st.session_state.dados_fc.get(linha_selecionada, {}):
                        valor_atual = st.session_state.dados_fc[linha_selecionada][mes_selecionado]
                    else:
                        valor_atual = 0

                    novo_valor = st.number_input("Novo Valor", value=float(valor_atual), key="valor_edit")

                col_salvar, col_deletar = st.columns(2)

                with col_salvar:
                    if st.button("Atualizar", key="btn_atualizar"):
                        st.session_state.dados_fc[linha_selecionada][mes_selecionado] = novo_valor
                        salvar_dados(st.session_state.dados_fc)
                        st.success(f"Atualizado: {linha_selecionada} em {mes_selecionado}")
                        st.rerun()

                with col_deletar:
                    if st.button("Deletar", key="btn_deletar"):
                        if mes_selecionado in st.session_state.dados_fc[linha_selecionada]:
                            del st.session_state.dados_fc[linha_selecionada][mes_selecionado]
                            salvar_dados(st.session_state.dados_fc)
                            st.success(f"Deletado: {linha_selecionada} em {mes_selecionado}")
                            st.rerun()
                        else:
                            st.error("Nada para deletar")
        else:
            st.info("Nenhum dado para editar")

    st.markdown("---")
    st.markdown("## Gerenciamento de Dados")

    with st.expander("Limpar/Deletar Dados"):
        st.warning("Use com cuidado - essas ações são irreversíveis!")

        col_acao, col_btn = st.columns(2)

        with col_acao:
            acao = st.radio(
                "Selecione a ação:",
                ["Deletar dados de um mes", "Limpar TODOS os dados"],
                key="acao_limpeza"
            )

        if acao == "Deletar dados de um mes":
            meses_existentes = sorted(set(m for k, v in st.session_state.dados_fc.items() if k != "orcamento" for m in v.keys()))

            if meses_existentes:
                mes_deletar = st.selectbox("Selecione o mes para deletar", meses_existentes, key="mes_deletar")

                if st.button("Deletar Dados de " + mes_deletar, key="btn_deletar_mes"):
                    for linha in [k for k in st.session_state.dados_fc.keys() if k != "orcamento"]:
                        if mes_deletar in st.session_state.dados_fc[linha]:
                            del st.session_state.dados_fc[linha][mes_deletar]

                    salvar_dados(st.session_state.dados_fc)
                    st.success(f"Dados de {mes_deletar} deletados!")
                    st.rerun()
            else:
                st.info("Nenhum mes para deletar")

        else:
            if st.button("DELETAR TODOS OS DADOS", key="btn_deletar_todos"):
                st.session_state.dados_fc = {}
                salvar_dados(st.session_state.dados_fc)
                st.success("Todos os dados foram deletados!")
                st.rerun()


# Processar dados para mostrar
if st.session_state.dados_fc:
    st.info(f"Mes Atual: {mes_atual}")

    # Metricas
    col1, col2, col3, col4 = st.columns(4)

    receitas = 0
    despesas = 0
    for k, v in st.session_state.dados_fc.items():
        if k != "orcamento":
            valor = v.get(mes_atual, 0)
            if valor > 0:
                receitas += valor
            else:
                despesas += abs(valor)

    saldo = receitas - despesas

    col1.metric("Receitas", f"R$ {receitas:,.0f}")
    col2.metric("Despesas", f"R$ {despesas:,.0f}")
    col3.metric("Saldo", f"R$ {saldo:,.0f}")
    col4.metric("Status", "OK")

    # Tabs
    tab_dados, tab_graficos = st.tabs(["Planilha", "Graficos"])

    with tab_dados:
        st.markdown("### Tabela - Fluxo de Caixa por Mes")

        # Gerenciar Meses - Botões acima da tabela
        meses_existentes = sorted(set(m for k, v in st.session_state.dados_fc.items() if k != "orcamento" for m in v.keys()))

        if meses_existentes:
            st.markdown("**Deletar Colunas:** Clique no X para remover um período")
            col_meses = st.columns(len(meses_existentes) + 1)

            for idx, mes in enumerate(meses_existentes):
                with col_meses[idx]:
                    st.markdown(f"<div style='text-align: center;'><b>{mes}</b></div>", unsafe_allow_html=True)
                    if st.button("✕", key=f"del_{mes}", help=f"Deletar {mes}"):
                        for linha in list(st.session_state.dados_fc.keys()):
                            if linha != "orcamento" and mes in st.session_state.dados_fc[linha]:
                                del st.session_state.dados_fc[linha][mes]
                        salvar_dados(st.session_state.dados_fc)
                        st.success(f"✅ {mes} deletado!")
                        st.rerun()

            with col_meses[-1]:
                st.markdown("<div style='text-align: center;'><b>Novo</b></div>", unsafe_allow_html=True)
                if st.button("➕", key="btn_add_new_mes"):
                    st.session_state.show_novo_mes = True

            # Form para novo mês
            if st.session_state.get('show_novo_mes'):
                st.markdown("---")
                col_novo_mes, col_novo_ano, col_criar = st.columns([1, 1, 1])

                with col_novo_mes:
                    novo_mes = st.selectbox("Mes", range(1, 13), format_func=lambda x: f"{x:02d}", key="novo_mes_sel")

                with col_novo_ano:
                    novo_ano = st.number_input("Ano", value=2026, min_value=2020, max_value=2030, key="novo_ano_sel")

                with col_criar:
                    if st.button("Criar"):
                        mes_novo = f"{novo_ano}-{novo_mes:02d}"
                        if mes_novo not in meses_existentes:
                            for linha in list(st.session_state.dados_fc.keys()):
                                if linha != "orcamento":
                                    st.session_state.dados_fc[linha][mes_novo] = 0.0
                            salvar_dados(st.session_state.dados_fc)
                            st.session_state.show_novo_mes = False
                            st.success(f"✅ {mes_novo} criado!")
                            st.rerun()
                        else:
                            st.error(f"⚠️ {mes_novo} já existe!")

            st.markdown("---")

        # Criar DataFrame pivotado
        dados_lista = []
        for linha, valores_mes in st.session_state.dados_fc.items():
            if linha == "orcamento":
                continue
            row = {"Linha": linha}
            row.update(valores_mes)
            dados_lista.append(row)

        if dados_lista:
            df_tabela = pd.DataFrame(dados_lista)

            # Ordena colunas por mes (YYYY-MM cronologicamente)
            cols_mes = [col for col in df_tabela.columns if col != "Linha" and len(col) == 7 and re.match(r'^\d{4}-\d{2}$', col)]
            cols_mes_ordenado = sorted(cols_mes)  # YYYY-MM ordena alfabeticamente também cronologicamente

            if cols_mes_ordenado:
                df_tabela = df_tabela[["Linha"] + cols_mes_ordenado]

                # Calcula receitas e despesas por mês
                receitas_por_mes = {}
                despesas_por_mes = {}
                saldo_por_mes = {}

                for mes in cols_mes_ordenado:
                    receitas = df_tabela[df_tabela[mes] > 0][mes].sum()
                    despesas = abs(df_tabela[df_tabela[mes] < 0][mes].sum())
                    saldo = receitas - despesas

                    receitas_por_mes[mes] = receitas
                    despesas_por_mes[mes] = despesas
                    saldo_por_mes[mes] = saldo

                # Adiciona linhas de totais
                df_display = df_tabela.copy()

                # Linha de Receitas
                receitas_row = {"Linha": "TOTAL RECEITAS"}
                for mes in cols_mes_ordenado:
                    receitas_row[mes] = receitas_por_mes[mes]
                df_display = pd.concat([df_display, pd.DataFrame([receitas_row])], ignore_index=True)

                # Linha de Despesas
                despesas_row = {"Linha": "TOTAL DESPESAS"}
                for mes in cols_mes_ordenado:
                    despesas_row[mes] = -despesas_por_mes[mes]
                df_display = pd.concat([df_display, pd.DataFrame([despesas_row])], ignore_index=True)

                # Linha de Saldo Final
                saldo_row = {"Linha": "SALDO FINAL"}
                for mes in cols_mes_ordenado:
                    saldo_row[mes] = saldo_por_mes[mes]
                df_display = pd.concat([df_display, pd.DataFrame([saldo_row])], ignore_index=True)

                # Formata para exibição
                df_display = df_display[["Linha"] + cols_mes_ordenado]

                # Cria styler apenas com formatação de número (sem cores)
                styler = df_display.set_index("Linha").style.format('R$ {:,.0f}')

                # Apenas negrito nas linhas de totais (sem background)
                def highlight_totals(s):
                    if s.name in ["TOTAL RECEITAS", "TOTAL DESPESAS", "SALDO FINAL"]:
                        return ["font-weight: bold"] * len(s)
                    return [""] * len(s)

                styler = styler.apply(highlight_totals, axis=1)

                st.dataframe(styler, use_container_width=True)
            else:
                st.dataframe(df_tabela, use_container_width=True)


    with tab_graficos:
        st.markdown("### Evolucao de Custos - Tendencia por Mes")

        # Gráfico de linha
        meses_disponiveis = sorted(set(m for k, linha in st.session_state.dados_fc.items() if k != "orcamento" for m in linha.keys()))

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

        st.markdown("### Heatmap - Intensidade de Gastos por Mes")

        if meses_disponiveis:
            dados_heatmap = []
            linhas_principais = sorted([k for k in st.session_state.dados_fc.keys() if k != "orcamento"],
                                      key=lambda x: abs(st.session_state.dados_fc[x].get(mes_atual, 0)),
                                      reverse=True)[:10]

            for linha in linhas_principais:
                valores = [st.session_state.dados_fc[linha].get(mes, 0) for mes in meses_disponiveis]
                dados_heatmap.append(valores)

            fig_heatmap = go.Figure(data=go.Heatmap(
                z=dados_heatmap,
                x=meses_disponiveis,
                y=[l[:25] for l in linhas_principais],
                colorscale='Greys',
            ))

            fig_heatmap.update_layout(height=300, margin=dict(l=150, r=0, t=0, b=0))
            st.plotly_chart(fig_heatmap, use_container_width=True)

        st.markdown("### Orcado vs Realizado - % de Uso")

        if "orcamento" in st.session_state.dados_fc:
            dados_orcamento = []

            for linha, valores_mes in st.session_state.dados_fc.items():
                if linha == "orcamento":
                    continue

                realizado = abs(valores_mes.get(mes_atual, 0))
                orcado = abs(st.session_state.dados_fc["orcamento"].get(linha, {}).get(mes_atual, 0))

                if orcado > 0:
                    pct_uso = (realizado / orcado * 100)
                    dados_orcamento.append({
                        "Linha": linha,
                        "Orcado": orcado,
                        "Realizado": realizado,
                        "% Uso": pct_uso,
                        "Status": "OK" if pct_uso <= 100 else "Acima"
                    })

            if dados_orcamento:
                df_orcamento = pd.DataFrame(dados_orcamento)
                df_orcamento = df_orcamento.sort_values("Realizado", ascending=True)

                fig_orcamento = go.Figure()

                fig_orcamento.add_trace(go.Bar(
                    y=df_orcamento["Linha"],
                    x=df_orcamento["Orcado"],
                    orientation='h',
                    name='Orcado',
                    marker=dict(color='#D1D5DB'),
                ))

                fig_orcamento.add_trace(go.Bar(
                    y=df_orcamento["Linha"],
                    x=df_orcamento["Realizado"],
                    orientation='h',
                    name='Realizado',
                    marker=dict(color='#374151'),
                ))

                fig_orcamento.update_layout(
                    barmode='overlay',
                    height=400,
                    margin=dict(l=150, r=0, t=0, b=0),
                    hovermode='y unified'
                )

                st.plotly_chart(fig_orcamento, use_container_width=True)

                st.markdown("**Resumo de Uso:**")
                styler_orcamento = df_orcamento[["Linha", "Orcado", "Realizado", "% Uso"]].style.format({
                    "Orcado": "R$ {:,.0f}",
                    "Realizado": "R$ {:,.0f}",
                    "% Uso": "{:.1f}%"
                })
                st.dataframe(styler_orcamento, use_container_width=True)

else:
    st.info("Carregue um CSV ou adicione dados manualmente")
