# ☁️ Hospedando na Nuvem (FÁCIL!)

## O que seu pai/irmão farão

1. Recebem um **link** (tipo Gmail)
2. Clicam no link
3. Fazem upload do PDF do Sienge
4. Veem os gráficos

**PRONTO!** Nenhuma instalação, nenhum terminal.

---

## Como você cria esse link (1x, demora 10 min)

### Passo 1: Crie uma conta GitHub (GRÁTIS)

1. Vá em https://github.com/signup
2. Preencha:
   - Email: `seu_email@gmail.com`
   - Senha: `qualquer_coisa_segura`
   - Usuário: `seu_nome_ou_empresa` (vai aparecer na URL)
3. Confirme o email

### Passo 2: Suba o projeto no GitHub

Abra o **PowerShell** (uma última vez) na pasta do projeto:

```bash
cd "C:\Users\berna\Downloads\files\fluxo_caixa_automation"

git init
git add .
git commit -m "Dashboard FC inicial"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/fluxo-caixa-dashboard.git
git push -u origin main
```

(Substitua `SEU_USUARIO` pelo que criou no GitHub)

### Passo 3: Deploy na Streamlit Cloud (AUTOMÁTICO)

1. Vá em https://streamlit.io/cloud
2. Clique em **"Deploy an app"** (botão azul)
3. Conecte sua conta GitHub (autoriza o Streamlit)
4. Selecione:
   - Repository: `seu_usuario/fluxo-caixa-dashboard`
   - Branch: `main`
   - Main file path: `app.py`
5. Clique em **Deploy**

**Pronto!** Em 2 minutos, você recebe uma URL tipo:
```
https://fluxo-caixa-dashboard-seu_usuario.streamlit.app
```

### Passo 4: Compartilhe o link

Envie para seu pai/irmão:

> Ei, aqui está o dashboard:
> https://fluxo-caixa-dashboard-seu_usuario.streamlit.app
>
> Vocês acessam no navegador, fazem upload do PDF do Sienge,
> e veem os gráficos. Não precisa instalar nada!

---

## 🎯 Fluxo mensal (pra você)

```
1. Você recebe "Contas Pagas" do Sienge (PDF)
           ↓
2. Você sobe o PDF no site do dashboard (upload)
           ↓
3. Seu pai/irmão/financeiro acessam o link
           ↓
4. Já veem os gráficos atualizados (automático)
```

---

## ❓ Dúvidas Comuns

**P: Preciso de cartão de crédito pra Streamlit Cloud?**
Não! É grátis (até 3 apps simultâneos).

**P: E se eu mudar o código depois?**
Muda o arquivo no seu PC, faz `git push` → Streamlit redeploy automaticamente.

**P: Quanto tempo demora pra atualizar?**
2-3 minutos após você fazer push.

**P: E se o servidor cair?**
Streamlit é hospedado na nuvem da Streamlit Inc. (confiável). Backup automático.

**P: Como eles fazem upload do PDF?**
No app, tem um campo "Selecione o PDF" → clica e escolhe o arquivo no PC deles.

---

## 🔒 Segurança

- Link é público, mas **não é listado em lugar nenhum**
  - Só quem tiver o link acessa
  - Se quiser, pode adicionar senha (futura)
- Dados processados **não são salvos** no servidor
  - Só PDF é processado em memória e descartado
- Seu repositório GitHub pode ser **privado**

---

## 📊 Alternativa: Azure (se quiser mais segurança)

Se seu pai exigir mais "profissionalismo":

1. Crie conta Azure (grátis por 12 meses)
2. Deploy em **Azure Container Instances**
3. URL tipo: `https://fc-ville.brazilsouth.azurecontainer.io`

Mas é mais complexo. **Recomendo Streamlit Cloud** pra começar.

---

## ✅ Checklist Final

Antes de compartilhar o link:

- [ ] GitHub criado
- [ ] Repositório criado e feito push
- [ ] Streamlit Cloud conectado
- [ ] URL gerada (tipo `*.streamlit.app`)
- [ ] Testou clicando no link do navegador
- [ ] Uploadou um PDF de teste e viu os gráficos

**Pronto!** Compartilhe com seu pai/irmão.

---

## 📞 Se der erro

**"Repository not found"**
- Confirme que o repo existe em GitHub (https://github.com/seu_usuario/fluxo-caixa-dashboard)

**"app.py not found"**
- Confirme que o arquivo `app.py` está na raiz do repositório

**"ModuleNotFoundError"**
- Confirme que `requirements.txt` está na raiz

---

**Versão**: 1.0  
**Última atualização**: 2026-06-30  
**Tempo de setup**: ~10 minutos (1x)  
**Tempo mensal**: ~1 minuto (upload do PDF)
