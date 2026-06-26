# Como rodar no UiPath Studio (passo a passo)

Objetivo: ver o robô rodando de verdade. Siga em fases — cada fase só começa
quando a anterior funcionou. Se algo ficar vermelho, anote a mensagem.

---

## Fase 0 — Pré-requisitos (uma vez)

### 0.1 Orchestrator (Automation Cloud Community — grátis)
1. Acesse https://cloud.uipath.com → crie/entre no tenant.
2. **Tenant → Queues → Add**: nome `EmailWorkItems`,
   marque **Enforce unique references = Yes**, `Max # of retries = 2`.
3. **Tenant → Assets → Add**: tipo **Credential**, nome `ACME_Credential`,
   usuário/senha da sua conta ACME (ver 0.3).
4. No **UiPath Assistant** (bandeja do Windows) → **Sign In** no mesmo tenant.
   Isso conecta o Studio ao Orchestrator (necessário p/ Queue e Assets).

### 0.2 Gmail App Password (p/ o Dispatcher ler e-mails)
1. Conta Google de teste com **verificação em 2 etapas** ativada.
2. https://myaccount.google.com/apppasswords → gere uma senha de app (16 dígitos).
3. Crie as pastas/labels `Processed` e `Processed/Rejected` no Gmail.
4. Atualize `1.Dispatcher/Data/Config.xlsx` → `EmailAccount` com o e-mail.

### 0.3 Conta ACME (p/ o Performer)
1. Cadastre-se em https://acme-test.uipath.com (e-mail + senha).
2. Use esse login/senha no Asset `ACME_Credential` (passo 0.1.3).

---

## Fase 1 — Abrir e reparar o Dispatcher

1. Studio → **Open** → `1.Dispatcher/project.json`.
2. Se aparecer aviso de dependências: **Manage Packages → atualizar/Repair**
   (deixe o Studio resolver as versões instaladas na sua máquina).
3. Abra `Main.xaml` e `InitAllSettings.xaml`.
   - Os arquivos foram escritos à mão: o Studio pode marcar algum activity em
     vermelho (nome de propriedade/assinatura diferente da versão do pacote).
   - **Clique no activity vermelho** e veja a mensagem — me mande que eu ajusto.
4. **Ctrl+S** e use **Design → Analyze File** (Workflow Analyzer). Mire 0 erros.

> Dica: se preferir, recrie os dois activities de e-mail (Get IMAP / Move) e o
> Add Queue Item arrastando do painel Activities — os parâmetros (servidor,
> pasta, QueueName, ItemInformation) estão todos no `BuildGuide.md`.

---

## Fase 2 — Rodar o Dispatcher

1. Rode `tools/send_test_emails.py` (ou mande você mesmo 3-4 e-mails no formato
   `Type:/Vendor:/Description:`) para a caixa de teste.
2. No Studio: **Run** (F5) no `Main.xaml`.
3. **Resultado esperado:** no Output, "Enfileirados: 3 | Rejeitados: 1".
   No Orchestrator → Queues → `EmailWorkItems`: 3 itens **New**.

---

## Fase 3 — Criar e rodar o Performer (REFramework)

1. Studio → **New Project → Robotic Enterprise Process** → nome `EmailToACME.Performer`.
2. Substitua o `Data/Config.xlsx` gerado pelo deste repo (`2.Performer/Data/Config.xlsx`).
3. Copie para a pasta do projeto: `Process.xaml`, `System1_Login.xaml`,
   `System1_CreateWorkItem.xaml` (e `Tests/Test_Process.xaml`).
4. Edite `Framework/InitAllApplications.xaml` (ver `BuildGuide.md`):
   - `Get Credential` do Asset `ACME_Credential`.
   - `Open Browser` em `Config("ACME_URL")` → invoca `System1_Login.xaml`.
   - Guarde o Browser em `Config("ACME_Browser")` (o `Process.xaml` lê de lá).
5. Em `Main.xaml` (template), confirme `Config("OrchestratorQueueName") = EmailWorkItems`.
6. **Run** (F5). O REFramework vai consumir a fila, logar no ACME e criar os Work Items.
7. **Resultado esperado:** itens da Queue viram **Successful**; no ACME aparecem
   os Work Items criados. Force um erro (vendor inválido) p/ ver Business Exception.

---

## Se travar

Cole aqui a mensagem do activity vermelho ou do Output. Os pontos mais prováveis:
- Versão de pacote diferente → Manage Packages / Repair.
- Assinatura de activity de e-mail (IMAP) diferente da sua versão → recriar arrastando.
- Argumentos do Invoke Workflow → reabrir o Invoke e remapear (Import Arguments).
