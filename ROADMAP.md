# 🗺️ Roadmap - Fluxo de Caixa Dashboard

## ✅ FASE 1: Extração + Dashboard Básico (CONCLUÍDA)

- [x] Script Python que extrai PDF do Sienge
- [x] Gera CSV estruturado (long format)
- [x] Dashboard Streamlit com 2 abas (FC + Análise)
- [x] Gráficos iniciais (pizza, barras, KPIs)
- [x] Export para Excel
- [x] Clique-duplo executável (.bat)
- [x] Deploy pronto pra nuvem (Azure/Streamlit Cloud)

**Status**: 🟢 Pronto para uso

---

## 📋 FASE 2: Entradas de Dados Manuais (PRÓXIMA)

Permitir que usuários adicionem dados que não vêm do Sienge (receitas, ajustes, projeções manuais).

### 2.1 Interface de Input
- [ ] Sidebar com abas: "Sienge" | "Entrada Manual" | "Projeções"
- [ ] Formulário no Streamlit:
  - Data
  - Centro de Custo / Categoria
  - Descrição
  - Valor
  - Tipo (Receita / Despesa / Ajuste)
- [ ] Botão "Adicionar" → salva em `dados_manuais.csv`

### 2.2 Consolidação de Dados
- [ ] Função que mescla `fc_dados.csv` (Sienge) + `dados_manuais.csv` (entrada manual)
- [ ] Evita duplicatas
- [ ] Permite editar/deletar entradas manuais

### 2.3 Storage Local
- [ ] CSV local (`dados_manuais.csv`) salva as entradas
- [ ] Persiste entre execuções do app

**Esforço**: ~4-6 horas  
**Prioridade**: 🔴 ALTA

---

## 📈 FASE 3: Receitas & Projeções

### 3.1 Receitas (Vendas)
- [ ] Campo para projetar vendas mensais
- [ ] Slider ou input manual: "Quantidade de lotes × Preço"
- [ ] Integração com dados históricos (se tiver)
- [ ] Visualização: linha de tendência (realizado vs. projetado)

### 3.2 Projeções de Despesas
- [ ] Multiplicadores por categoria (ex: "Stand" cresce 5% ao mês)
- [ ] Modo "Cenários": 3 planilhas (Otimista, Base, Pessimista)
- [ ] What-if: "E se cortar 20% de Marketing?"

### 3.3 Saldo Projetado
- [ ] Gráfico de linha: Saldo acumulado (realizado + projetado)
- [ ] Highlight de ponto de break-even (se houver)
- [ ] Tabela mensal: Receita | Despesa | Saldo | % Meta

**Esforço**: ~8-10 horas  
**Prioridade**: 🟠 MÉDIA

---

## 🎨 FASE 4: Melhorar Gráficos (PARALELO)

### 4.1 Gráficos Novos
- [ ] **Waterfall** (Saldo Anterior + Receitas - Despesas = Saldo Novo)
- [ ] **Gauge/Speedometer** (% de meta de receita)
- [ ] **Heatmap** (Categoria × Mês, mostrando evolução)
- [ ] **Sankey** (Fluxo de dinheiro entre categorias)
- [ ] **Box Plot** (Dispersão de despesas por mês)

### 4.2 Melhorias Visuais
- [ ] Cores mais profissionais (brand da Ville)
- [ ] Temas: Light / Dark mode
- [ ] Gráficos maiores e responsivos
- [ ] Legenda interativa (clique pra filtrar)
- [ ] Anotações (ex: "Evento especial em abril")

### 4.3 Interatividade
- [ ] Drill-down: Clica em "Marketing" → detalha os gastos
- [ ] Range de datas customizável
- [ ] Comparação de períodos (abril/2026 vs. março/2026)

**Esforço**: ~6-8 horas  
**Prioridade**: 🟠 MÉDIA

---

## 🔗 FASE 5: Integração com Outras Fontes

### 5.1 Bancos
- [ ] Importar extratos OFX (Bradesco, Itaú, etc.)
- [ ] Reconciliação automática com despesas lançadas

### 5.2 NF-e / XML
- [ ] Ler XMLs de notas fiscais
- [ ] Extrair valor, fornecedor, data
- [ ] Auto-preencher FC

### 5.3 Google Sheets
- [ ] Ler dados de planilhas compartilhadas
- [ ] Atualizar em tempo real (sem baixar CSV)

### 5.4 API Sienge (Futuro)
- [ ] Eliminar download manual do PDF
- [ ] Pull automático diário/semanal

**Esforço**: ~12-16 horas  
**Prioridade**: 🟡 BAIXA

---

## 🚀 FASE 6: Deployment & Compartilhamento

### 6.1 Nuvem
- [ ] Deploy no Azure Container Instances
- [ ] URL pública para pai/irmão/financeiro
- [ ] Login com Microsoft 365 (opcional)

### 6.2 Notifications
- [ ] Alertas quando despesa > threshold
- [ ] E-mail semanal com resumo
- [ ] Slack integration

### 6.3 Backup & Histórico
- [ ] Backup automático dos dados (Azure Storage)
- [ ] Versionamento de histórico
- [ ] Rollback se necessário

**Esforço**: ~4-6 horas  
**Prioridade**: 🟡 BAIXA

---

## 📊 Priorização Recomendada

**Curto prazo (Próximas 2 semanas)**:
1. ✍️ FASE 2: Entrada Manual (essencial pra controle)
2. 🎨 FASE 4: Melhorar Gráficos (visual)

**Médio prazo (Próximas 4 semanas)**:
3. 📈 FASE 3: Projeções (estratégico)
4. 🔗 FASE 5: Integração com Bancos (facilita)

**Longo prazo**:
5. 🚀 FASE 6: Cloud & Compartilhamento (escalabilidade)

---

## 💡 Notas Técnicas

### Stack Mantida
- Python 3.13 (produção)
- Streamlit (interface)
- Plotly (gráficos)
- Pandas (dados)
- CSV local (storage)

### Melhorias Possíveis
- Migrar storage CSV → SQLite (mais robusto)
- Banco de dados: PostgreSQL (se nuvem)
- Cache: Redis (performance)
- Testes automatizados (unittest/pytest)

### Escalabilidade
- App atual roda 100K linhas sem problema
- Multi-user: precisa de permissões (fase 6)
- Mobile: Streamlit tem suporte nativo

---

## 📞 Próximos Passos

1. Você testar o dashboard FASE 1 com dados de abril/2026
2. Feedback sobre gráficos (quais melhorar?)
3. Priorizar FASE 2 vs FASE 4 (entrada manual ou gráficos?)
4. Agendar desenvolvimento

---

**Última atualização**: 2026-06-30  
**Estimativa total**: ~32-40 horas para todas as fases  
**Status geral**: 🟢 Fase 1 completa, pronto para Fase 2
