# 🎯 Dashboard Streamlit - Guia de Uso

## O que é?

Um dashboard web interativo construído em Python + Streamlit. Substitui o Excel + Power BI por uma interface moderna, rápida e sem instalações complexas.

## ⚡ Início rápido (Local)

### 1. Instalar dependências

```bash
cd C:\Users\berna\Downloads\files\fluxo_caixa_automation
pip install -r requirements.txt
```

### 2. Gerar dados (se ainda não tiver)

```bash
python sienge_to_bi.py "C:\Users\berna\Downloads\CONTAS PAGAS.pdf" "" "output\fc_dados.csv"
```

Isso cria `output/fc_dados.csv` com os dados do mês.

### 3. Rodar o app

```bash
streamlit run app.py
```

Pronto! O navegador abre em **http://localhost:8501** 🎉

---

## 🎨 Interface

### Sidebar (esquerda)
- **Upload de CSV**: Carrega dados do Sienge
- **Filtros**: Seleciona categorias pra visualizar
- **Info do período**: Mostra mês dos dados

### Aba 1: Fluxo de Caixa
- **Tabela** com todas as linhas de despesa
- **Valores formatados** em R$
- **Botão de download** → Excel (compatível com FCVILLE)

### Aba 2: Análise
- **4 cartões KPI**: Total, Receitas, Despesas, Saldo
- **Pizza**: Distribuição por categoria
- **Barras**: Top 5 maiores despesas
- **Tabela**: Resumo por categoria

---

## 📤 Deploy no Azure (Nuvem)

Para seu pai/irmão/financeiro acessarem de qualquer lugar, sem instalar nada:

### Opção A: Azure Container Instances (Fácil)

1. **Crie um arquivo `Dockerfile`** na pasta raiz:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

2. **Faça login no Azure**:

```bash
az login
```

3. **Crie um Resource Group**:

```bash
az group create --name fc-dashboard --location brazilsouth
```

4. **Faça build e push da imagem**:

```bash
az acr create --resource-group fc-dashboard --name fcdashboard --sku Basic
az acr build --registry fcdashboard --image fc-app:latest .
```

5. **Deploy no Container Instances**:

```bash
az container create \
  --resource-group fc-dashboard \
  --name fc-app \
  --image fcdashboard.azurecr.io/fc-app:latest \
  --cpu 1 --memory 1 \
  --ports 8501 \
  --registry-login-server fcdashboard.azurecr.io \
  --registry-username <username> \
  --registry-password <password>
```

6. **Pega a URL pública**:

```bash
az container show --resource-group fc-dashboard --name fc-app --query ipAddress.fqdn
```

Pronto! Compartilhe essa URL com seu pai/irmão.

---

### Opção B: Streamlit Cloud (Mais simples)

1. **Suba o projeto no GitHub**:

```bash
git init
git add .
git commit -m "Dashboard FC inicial"
git remote add origin https://github.com/seu-usuario/fluxo-caixa-dashboard
git push -u origin main
```

2. **Vá em [streamlit.io/cloud](https://streamlit.io/cloud)**
3. **Clique "Deploy an app"**
4. **Conecte seu repositório GitHub**
5. **Selecione `main` branch e arquivo `app.py`**
6. **Deploy automático** (Streamlit cria a URL pública)

Compartilhe o link gerado com seu pai/irmão — eles acessam direto no navegador.

---

## 🔄 Fluxo mensal

```
1. Baixa "Contas Pagas" do Sienge (PDF)
       ↓
2. Roda: python sienge_to_bi.py "CONTAS PAGAS.pdf" "" "output/fc_dados.csv"
       ↓
3. Acessa o dashboard (local ou nuvem)
       ↓
4. Seu pai/irmão/financeiro já veem dados atualizados
```

---

## 💡 Customizações

### Mudar cores do theme

No `app.py`, seção `st.markdown()` com `<style>`, altere as variáveis CSS:

```css
--primary-color: #0066cc;      /* Azul */
--secondary-color: #27ae60;    /* Verde */
--danger-color: #e74c3c;       /* Vermelho */
```

### Adicionar novo gráfico

Exemplo: Gráfico de linha (evolução mensal):

```python
fig_linha = px.line(
    df_filtrado.groupby('Data')['Valor'].sum().reset_index(),
    x='Data',
    y='Valor',
    title='Evolução do Saldo',
    markers=True
)
st.plotly_chart(fig_linha, use_container_width=True)
```

### Adicionar nova métrica

No KPI Cards da Aba 2:

```python
with col5:
    st.metric(
        "Maior Despesa",
        f"R$ {dados['por_linha']['Valor'].min():,.2f}",
    )
```

---

## 🆘 Troubleshooting

**P: Streamlit não encontrado**
```bash
pip install streamlit
```

**P: Erro "ModuleNotFoundError: No module named 'plotly'"**
```bash
pip install plotly
```

**P: O CSV não carrega**
- Confirme que o arquivo existe em `output/fc_dados.csv`
- Verifique se o caminho está correto

**P: Quer adicionar outro arquivo/fonte?**
- Edite `sienge_to_bi.py` → seção `parse_sienge_pdf()`
- Estenda o dicionário `CC_TO_ROW` com novos centros de custo

---

## 📊 Dados do CSV esperado

O app espera um CSV com estas colunas:

| Data | CentroCusto | Categoria | DescricaoLinha | Valor |
|---|---|---|---|---|
| 2026-04-01 | 5001 | Receita de Vendas | Comissões S/ Venda | 53804.18 |
| 2026-04-01 | 5007 | Custos de Obra | OBRA | 1980062.84 |

Gerado automaticamente pelo `sienge_to_bi.py` ✅

---

## 🚀 Performance

- **Carregamento**: < 2 segundos (local)
- **Filtros**: Tempo real
- **Gráficos**: Interativos (zoom, hover, download PNG)
- **Excel**: Gerado em < 1 segundo

---

## 📞 Suporte

Se der erro, confira:

1. Python 3.7+ instalado: `python --version`
2. Dependências instaladas: `pip list | grep streamlit`
3. Arquivo CSV existe: `ls output/fc_dados.csv`
4. Porta 8501 não bloqueada: `netstat -ano | findstr :8501`

---

**Versão**: 1.0  
**Última atualização**: 2026-06-30  
**Status**: Pronto para uso
