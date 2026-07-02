# Persistência de Dados em GitHub

Os dados agora são salvos permanentemente em **GitHub**, garantindo que nunca se percam mesmo que o Streamlit Cloud seja reiniciado.

## Como Configurar

### 1. Criar um Token GitHub

1. Acesse: https://github.com/settings/tokens
2. Clique em **"Generate new token"** → **"Personal access tokens"**
3. Escolha **"Fine-grained tokens"**
4. Configure:
   - **Repository access**: Selecione um repositório privado (ou crie um novo)
   - **Permissions**: 
     - `contents: read, write` (para ler/escrever arquivos)
5. Copie o token (só aparece uma vez!)

### 2. Criar Repositório Privado de Dados (opcional)

Se preferir dados em um repo separado:

```bash
# No GitHub, crie um repo privado chamado "fluxo-caixa-dados"
# Não é necessário adicionar nada, deixa vazio
```

### 3. Configurar Secrets no Streamlit Cloud

1. Vá para: https://share.streamlit.io/settings
2. Selecione o app "fluxo-caixa-dashboard"
3. Clique em **"Secrets"**
4. Adicione:

```toml
github_token = "seu_token_aqui"
github_repo = "seu_usuario/fluxo-caixa-dados"
```

**Exemplo:**
```toml
github_token = "ghp_aBcDeFgHiJkLmNoPqRsTuVwXyZ123456789"
github_repo = "betascap/fluxo-caixa-dados"
```

### 4. Pronto! ✅

- Dados são salvos automaticamente no GitHub
- Se o Streamlit Cloud cair, dados são restaurados
- Histórico completo no Git

## Como Funciona

1. **Ao iniciar**: App tenta carregar dados do GitHub
2. **Ao salvar**: Dados são enviados para GitHub (auto-backup)
3. **Fallback**: Se GitHub falhar, usa arquivo local

## Verificar Dados

Os dados estão salvos em:
```
https://github.com/seu_usuario/fluxo-caixa-dados/blob/main/dados_fc.json
```

## Segurança

- ✅ Token é privado (armazenado no Streamlit Secrets)
- ✅ Repo pode ser privado
- ✅ Não há exposição de dados

---

**Pronto! Seus dados agora são permanentes.** 🔐
