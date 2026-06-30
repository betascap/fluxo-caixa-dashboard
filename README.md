# Automação de Fluxo de Caixa - Sienge → Power BI

Sistema de geração de Dashboard BI para acompanhamento de fluxo de caixa, alimentado por relatórios do Sienge.

## 📁 Estrutura do Projeto

```
fluxo_caixa_automation/
├── sienge_to_bi.py                 # Script principal (extrai PDF, gera CSV)
├── RODAR_SIENGE_TO_CSV.bat         # Clique-duplo para executar (Windows)
├── README.md                       # Este arquivo
├── README_POWERBI.md               # Guia passo-a-passo Power BI
├── MEDIDAS_POWERBI.dax             # Medidas prontas para copiar/colar
│
├── relatorios/                     # Pasta: PDFs do Sienge
│   └── CONTAS PAGAS.pdf            # Relatório mensal (baixar do Sienge)
│
├── planilhas_internas/             # Pasta: Planilhas complementares (futura)
│   └── (deixar vazia por enquanto)
│
├── nfes/                           # Pasta: Notas fiscais (futura)
│   └── (deixar vazia por enquanto)
│
└── output/                         # Pasta: Arquivos gerados
    ├── fc_dados.csv                # Dados estruturados para Power BI
    └── FCVILLE_OUTPUT.xlsx         # Excel atualizado (compatibilidade)
```

## 🚀 Início rápido

### Opção 1: Clique-duplo (mais fácil)

1. Coloque o PDF `CONTAS PAGAS.pdf` em `relatorios/`
2. Clique-duplo em `RODAR_SIENGE_TO_CSV.bat`
3. Responda as 3 perguntas (caminhos dos arquivos)
4. Pronto! `fc_dados.csv` foi gerado em `output/`

### Opção 2: Terminal (mais controle)

```bash
cd C:\Users\berna\Downloads\files\fluxo_caixa_automation
python sienge_to_bi.py "relatorios\CONTAS PAGAS.pdf" "" "output\fc_dados.csv"
```

## 📊 Próximo passo: Power BI

Veja [README_POWERBI.md](README_POWERBI.md) para:
- Importar `fc_dados.csv` no Power BI Desktop
- Criar as abas de FC e Gráficos
- Compartilhar com sócios/financeiro via Power BI Service

## 📝 Como funciona

### 1. Extração (Python)

```
PDF do Sienge (Contas Pagas)
       ↓
  Lê centro de custo + valor líquido
       ↓
  Agrupa por categoria
       ↓
  Gera CSV estruturado (long format)
```

### 2. Visualização (Power BI)

```
CSV (fc_dados.csv)
       ↓
  Power BI Desktop importa
       ↓
  Cria modelo de dados
       ↓
  Desenha tabelas e gráficos
       ↓
  Publica no Power BI Service (nuvem)
       ↓
  Compartilha link com sócios/financeiro
```

## 🔄 Fluxo mensal

1. **Dia X do mês**: Você exporta "Contas Pagas" do Sienge (PDF)
2. **Dia X+1**: Coloca o PDF na pasta `relatorios/`, clica no `.bat`
3. **Dia X+2**: Abre Power BI Desktop, Refresh nos dados, verifica gráficos
4. **Dia X+3**: Publica no Power BI Service → pai/irmão/financeiro já veem atualizado

## 📋 Dados extraídos

Atualmente, o script extrai estes centros de custo do Sienge e mapeia para o FC:

| CC Sienge | Descrição | Linha do FC |
|---|---|---|
| 5001 | Receita de Vendas | Comissões S/ Venda |
| 5002 | Administrativo | Outras Despesas (adm) |
| 5003 | Comercial | Comissões S/ Venda |
| 5004 | Marketing | Marketing |
| 5005 | Stand de Vendas | Stand de Venda - Manutenção |
| 5006 | Incorporação | Incorporação |
| 5007 | Custos de Obra | OBRA - (revisão ABRIL/26) |
| 5009 | Terreno | IPTU Estoque |
| 5014 | Impostos | Impostos |
| 5015 | Clientes (ITBI) | ITBI |

### Para adicionar novos centros

Edite `sienge_to_bi.py`, seção `CC_TO_ROW`:

```python
CC_TO_ROW = {
    "5001": (25, "Receita de Vendas", "Comissões S/ Venda (Equipe Interna)"),
    "NOVO": (row_num, "Categoria", "DescricaoLinha"),  # ← Adicione aqui
    ...
}
```

## ⚙️ Dependências

- Python 3.7+
- `pdfplumber` — lê PDFs
- `openpyxl` — lê/escreve Excel
- Power BI Desktop (gratuito, Windows)
- Conta Power BI Service (para compartilhar)

Instalar:
```bash
pip install pdfplumber openpyxl
```

## 🔮 Futuras integrações

- [ ] Ler NF-e diretamente (XML)
- [ ] Integrar com API Sienge (sem baixar PDF)
- [ ] Bancos (extratos OFX)
- [ ] Google Sheets como entrada
- [ ] Alertas automáticos (Slack/Email)
- [ ] Cenários (vs orçado, vs mês anterior)

## 📞 Suporte

Se der erro, veja:

1. **Python não encontrado**: instale de [python.org](https://www.python.org/downloads/)
2. **PDF não encontrado**: verifique o caminho completo
3. **Erro no Power BI**: veja a seção de Troubleshooting em [README_POWERBI.md](README_POWERBI.md)

---

**Criado em**: 2026-06-30  
**Última atualização**: 2026-06-30  
**Status**: Fase 1 (extração + CSV) completa. Pronto para Power BI.
