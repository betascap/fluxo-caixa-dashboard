# Dashboard BI - Fluxo de Caixa

## Como usar

### 1. Atualizar dados (mensal)

```bash
python sienge_to_bi.py "CONTAS PAGAS.pdf" "FCVILLE_OUTPUT.xlsx" "fc_dados.csv"
```

Isso gera (ou atualiza) o arquivo `fc_dados.csv` com os dados mais recentes do Sienge.

### 2. Abrir Power BI Desktop

- Baixe e instale [Power BI Desktop](https://powerbi.microsoft.com/en-us/desktop/) (gratuito)
- Abra um novo projeto

### 3. Importar os dados

1. Home → `Obter Dados` → `Arquivo de Texto/CSV`
2. Selecione `fc_dados.csv`
3. Clique em `Carregar`
4. No painel direito, expanda a tabela e confirme que as colunas aparecem:
   - Data (data)
   - CentroCusto (texto)
   - Categoria (texto)
   - DescricaoLinha (texto)
   - Valor (número)

### 4. Criar a visualização "Fluxo de Caixa" (Aba 1)

Crie uma **Tabela** com:
- Linhas: `DescricaoLinha`
- Valores: `Sum(Valor)` formatado como moeda

```
Comissões S/ Venda                    R$ 141.694,57
Stand de Venda - Manutenção           R$ 146.149,02
Marketing                             R$ 83.275,15
ITBI                                  R$ 73.115,61
IPTU Estoque                          R$ 38.162,09
OBRA - (revisão ABRIL/26)             R$ 1.980.062,84
Incorporação                          R$ 7.417,40
Outras Despesas (adm)                 R$ 567.905,93
Impostos                              R$ 277.617,70
```

### 5. Criar os gráficos (Aba 2 - "Análise")

#### Gráfico 1: Despesas por Categoria (Pizza)

- Legenda: `Categoria`
- Valores: `Sum(Valor)`
- Filtro: apenas valores ≠ 0

#### Gráfico 2: Top 5 Maior Gasto (Barra horizontal)

- Eixo Y: `DescricaoLinha`
- Eixo X: `Sum(Valor)` (em valor absoluto)
- Limite: top 5

#### Gráfico 3: Sumário (Cartões KPI)

Crie 3 cartões mostrando:
- **Total de Receitas**: `Sum(Valor)` onde `Categoria` = "Receita de Vendas" (se houver)
- **Total de Despesas**: `Sum(Valor)` onde `Categoria` ≠ "Receita"
- **Saldo**: Receitas - Despesas

### 6. Adicionar filtros interativos

- Crie um filtro de **Data** para que o usuário veja dados por período
- Crie um filtro de **Categoria** para drill-down

### 7. Exportar para Excel

Na aba de FC, clique nos **três pontos** (⋯) da tabela → **Exportar para Excel** para baixar os dados em .xlsx.

### 8. Publicar (Compartilhar com pai/irmão/financeiro)

1. Clique em `Publicar` (no Power BI Desktop, aba Home)
2. Escolha seu **workspace** (você pode criar um novo: "Fluxo de Caixa")
3. Clique em `Selecionar`
4. No Power BI Service (web), copie o link do relatório
5. Compartilhe com seu pai/irmão/financeiro — eles acessam via link (precisam de conta Microsoft/M365 da empresa)

---

## Estrutura dos dados (CSV)

Cada linha do CSV representa um lançamento do Sienge:

```
Data          → Data do relatório (YYYY-MM-DD)
CentroCusto   → Centro de custo Sienge (ex: 5001, 5002)
Categoria     → Categoria agrupada (ex: "Marketing", "Administrativo")
DescricaoLinha → Descrição exata da linha do FC (ex: "Marketing", "Stand de Venda - Manutenção")
Valor         → Valor líquido em reais (positivo ou negativo)
```

Quando você rodar o script novamente (próximo mês), o CSV é sobrescrito com os novos dados — basta fazer `Refresh` no Power BI Desktop pra atualizar.

---

## Troubleshooting

**P: O CSV não foi criado**
- Confirme que o PDF existe no caminho correto
- Rode: `python sienge_to_bi.py "C:\caminho\completo\CONTAS PAGAS.pdf"`

**P: Os valores estão zerados ou negativos**
- Isso é esperado — despesas aparecem negativas no template original
- No Power BI, você pode usar `ABS(Valor)` para mostrar valores absolutos

**P: Quero histórico de vários meses**
- Renomeie o CSV cada mês (ex: `fc_dados_2026_04.csv`, `fc_dados_2026_05.csv`)
- No Power BI, vá a Início → `Obter Dados` → `Combinar Arquivos` e selecione todos os CSVs da pasta
- Isso cria uma tabela única com histórico

---

## Próximas melhorias (futuro)

- [ ] Integração automática com Sienge via API (eliminar download manual do PDF)
- [ ] Gráficos de variância (realizado vs. orçado)
- [ ] Dashboard mobile (app Power BI)
- [ ] Alertas automáticos (ex: se despesa > 2M, notificar)
