# Guia de Build no UiPath Studio

Este guia recria o projeto no Studio. Os arquivos `.xaml` deste repositório servem
de referência — o **Performer** deve ser gerado a partir do template oficial do
REFramework e depois customizado (Process.xaml + workflows do System1).

---

## Parte 0 — Orchestrator (uma vez)

1. **Queue**: Tenant → Queues → Add → nome `EmailWorkItems`.
   - Marque **Enforce unique references = Yes** (idempotência via MessageId).
   - `Max # of retries = 2` (alinhado ao `MaxRetryNumber` do Config).
2. **Asset (Credential)**: Assets → Add → tipo *Credential* → nome `ACME_Credential`
   → usuário/senha da sua conta ACME.
3. Conecte o UiPath Assistant ao tenant (Sign In).

---

## Parte 1 — Dispatcher

Projeto **Process** simples (Sequence linear, sem framework).

### Variáveis (Main.xaml)
| Nome | Tipo | Default |
|------|------|---------|
| `Config` | `Dictionary(Of String, Object)` | — |
| `Messages` | `List(Of MailMessage)` | — |
| `AcceptedVendors` | `String()` | — |

### Passos
1. **Invoke `InitAllSettings`** (ou Read Range no Config.xlsx → `Config`).
   - Lê `Data/Config.xlsx`, abas `Settings` e `Constants` para o Dictionary `Config`.
2. **Get IMAP/Outlook Mail Messages**
   - Conta: `Config("EmailAccount").ToString`
   - Pasta: `Config("EmailReadFolder").ToString`
   - `Top = 50`, `OnlyUnreadMessages = True`, `MarkAsRead = False`
   - Saída → `Messages`.
3. **For Each `mail` In `Messages`** (TypeArgument: `MailMessage`)
   - **Try**
     - Parse do corpo → `WIType`, `Vendor`, `Description`
       (use `System.Text.RegularExpressions.Regex.Match(mail.Body, "Type:\s*(.+)").Groups(1).Value.Trim`).
     - **Validação** (If): campos não vazios **E** `AcceptedVendors.Contains(Vendor)`.
       - **Então**: `Add Queue Item`
         - QueueName: `Config("OrchestratorQueueName").ToString`
         - Reference: `mail.Headers("Message-ID")` (ou `mail.Subject & mail.Date.ToString`)
         - ItemInformation (Dictionary): WIType, Description, Vendor, EmailFrom=`mail.From`,
           EmailSubject=`mail.Subject`, ReceivedAt=`mail.Date.ToString("o")`.
         - **Move Mail** → pasta `Config("EmailProcessedFolder")`.
       - **Senão**: Move para `Processed/Rejected` + `Log Message` (Warn).
   - **Catch** `System.Exception` → `Log Message` (Error) + segue para o próximo.
4. **Log Message** (Info): `"Dispatcher finalizado. Enfileirados: " & count`.

> Dica: para Gmail use **App Password** (conta com 2FA) e IMAP `imap.gmail.com`.
> Para Outlook moderno, use as atividades **Office 365 / Microsoft Graph**.

---

## Parte 2 — Performer (REFramework)

### Gerar a base
`Studio → New Project → Robotic Enterprise Process`. Isso cria Main.xaml (state
machine) + a pasta `Framework/` com:
`InitAllSettings`, `InitAllApplications`, `GetTransactionData`,
`Process`, `SetTransactionStatus`, `CloseAllApplications`, `KillAllProcesses`,
`TakeScreenshot`, `RetryCurrentTransaction`.

Substitua o `Config.xlsx` gerado pelo deste repositório (`2.Performer/Data/Config.xlsx`).

### Customizações por arquivo

**`Framework/InitAllApplications.xaml`**
- Recebe `in_Config`.
- `Get Credential` (Orchestrator) do Asset `Config("ACME_Credential_Asset")` →
  `out`/`pwd` (SecureString).
- **Open Browser** em `Config("ACME_URL")` → invoca `System1_Login.xaml`
  (args: `in_Browser`, `in_Username`, `in_SecurePassword`).
- Guarda o `Browser` num argumento de saída/variável de aplicação.

**`Framework/GetTransactionData.xaml`** (já vem pronto p/ Queue)
- Confirme: `Get Transaction Item` da `Config("OrchestratorQueueName")`,
  saída `out_TransactionItem` (`QueueItem`). Quando `Nothing` → encerra o loop.

**`Process.xaml`** (este repositório traz uma referência) — **lógica de negócio**:
1. Lê do `in_TransactionItem`:
   - `WIType   = in_TransactionItem.SpecificContent("WIType").ToString`
   - `Descr    = in_TransactionItem.SpecificContent("Description").ToString`
   - `Vendor   = in_TransactionItem.SpecificContent("Vendor").ToString`
2. **Validação de negócio** (If): vendor habilitado no ACME?
   - Se não → **Throw** `New BusinessRuleException("Vendor nao habilitado: " & Vendor)`.
3. Invoca `System1_CreateWorkItem.xaml` (cria o WI no ACME, retorna `out_WIID`).
4. `Add Log Fields`: `WIID = out_WIID` para rastreabilidade.
5. `Log Message` (Info): `"Work Item criado: " & out_WIID`.

**`Framework/SetTransactionStatus.xaml`** (já trata os 3 caminhos)
- Success → `Set Transaction Status = Successful`.
- BusinessRuleException → `Failed / Business` (sem retry).
- Exception (System) → `Failed / Application` + retry até `MaxRetryNumber` +
  `TakeScreenshot`.

### Argumentos dos workflows do System1

`System1_Login.xaml`
| Arg | Dir | Tipo |
|-----|-----|------|
| in_Browser | In | `Browser` |
| in_Username | In | `String` |
| in_SecurePassword | In | `SecureString` |

`System1_CreateWorkItem.xaml`
| Arg | Dir | Tipo |
|-----|-----|------|
| in_Browser | In | `Browser` |
| in_WIType | In | `String` |
| in_Description | In | `String` |
| in_Vendor | In | `String` |
| out_WIID | Out | `String` |

---

## Parte 3 — Testes

- `Tests/Test_Process.xaml`: monta um `QueueItem` fake (Dictionary) e invoca
  `Process.xaml`, validando que `out_WIID` não é vazio.
- Use **Workflow Analyzer** (Design → Analyze) e mire **0 erros**.
- Rode o **Dispatcher** com 2–3 e-mails de teste, depois o **Performer**, e
  confira na Queue do Orchestrator: itens `Successful` e (se forçar erro) o retry.
