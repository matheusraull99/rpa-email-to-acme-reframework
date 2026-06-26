# EmailToACME — RPA UiPath (REFramework)

Automação **nível pleno** em UiPath que lê e-mails de uma caixa de entrada, extrai os
dados de Work Items e os lança no sistema web **ACME System 1**
(`https://acme-test.uipath.com`, ambiente oficial de treino da UiPath).

Arquitetura **Dispatcher + Performer** com **Orchestrator Queue**, seguindo o
**Robotic Enterprise Framework (REFramework)**.

> Projeto de **portfólio**. Usa apenas serviços/contas de teste — nenhum dado real.

---

## 1. Visão geral da arquitetura

```
                ┌───────────────────────┐
   E-mails ───► │  1.Dispatcher          │   lê e-mails não lidos,
   (inbox)      │  (Sequence linear)     │   valida e transforma cada
                │                        │   um em Queue Item
                └───────────┬────────────┘
                            │  Add Queue Item
                            ▼
                ┌───────────────────────┐
                │  Orchestrator Queue    │   EmailWorkItems
                │  (fila transacional)   │   (retry + SLA + auditoria)
                └───────────┬────────────┘
                            │  Get Transaction Item
                            ▼
                ┌───────────────────────┐
   ACME    ◄────│  2.Performer           │   consome a fila, faz login,
   System 1     │  (REFramework)         │   cria o Work Item, trata
                │                        │   exceções e dá retry
                └───────────────────────┘
```

**Por que separar Dispatcher e Performer?** É o padrão recomendado pela UiPath:
- O **Dispatcher** só coleta e enfileira (rápido, idempotente, baixo risco).
- O **Performer** processa item a item de forma resiliente — se um robô cair, a
  Queue garante que nada se perde e que os itens falhados podem ser reprocessados.
- Permite **escalar** (vários Performers consumindo a mesma fila) e **auditar**
  (cada transação fica registrada no Orchestrator).

---

## 2. Pré-requisitos

| Item | Versão / observação |
|------|---------------------|
| UiPath Studio | 2023.10+ (Community serve) |
| Pacotes | `UiPath.System.Activities`, `UiPath.UIAutomation.Activities`, `UiPath.Mail.Activities`, `UiPath.Excel.Activities` |
| Orchestrator | Cloud (Automation Cloud Community) ou on-prem |
| Conta de e-mail | Gmail/Outlook de **teste** (ver `Documentation/BuildGuide.md`) |
| Conta ACME | Grátis em https://acme-test.uipath.com (cadastro com e-mail) |

---

## 3. Setup rápido

1. **Orchestrator**
   - Crie a Queue `EmailWorkItems`.
   - Crie o Asset (Credential) `ACME_Credential` com login/senha do ACME.
   - Conecte o robô (Assistant) ao seu tenant.
2. **Config.xlsx** (em cada projeto, pasta `Data/`)
   - Ajuste `OrchestratorQueueName`, `ACME_URL`, conta de e-mail e pastas.
3. **Dispatcher** → rode `1.Dispatcher/Main.xaml` para popular a fila.
4. **Performer** → rode `2.Performer/Main.xaml` para consumir a fila.

Detalhes passo a passo (inclusive como recriar o REFramework a partir do template
oficial) estão em **`Documentation/BuildGuide.md`**.

---

## 4. Estrutura de pastas

```
EmailToACME-REFramework/
├── 1.Dispatcher/              Coleta e enfileiramento
│   ├── Main.xaml
│   ├── Data/Config.xlsx
│   └── project.json
├── 2.Performer/               Processamento transacional (REFramework)
│   ├── Main.xaml              (vem do template REFramework)
│   ├── Process.xaml           ← lógica de negócio (customizado)
│   ├── Framework/             InitAllSettings, GetTransactionData, etc.
│   ├── Data/Config.xlsx
│   ├── Tests/                 testes de workflow
│   └── project.json
└── Documentation/
    ├── PDD.md                 Process Definition Document (resumido)
    ├── QueueSchema.md         contrato dos dados na Queue
    └── BuildGuide.md          guia de construção no Studio
```

---

## 5. Boas práticas aplicadas (o que torna isso "pleno")

- **REFramework** com máquina de estados e retry por transação.
- **Separação Dispatcher/Performer** (padrão UiPath de produção).
- **Orchestrator Queue** em vez de planilha — auditoria, SLA e escalabilidade.
- **Business Rule Exception vs System Exception** tratadas de formas distintas.
- **Config.xlsx** externaliza toda configuração (zero hard-code).
- **Assets/Credentials** do Orchestrator — segredos fora do código.
- **Logging estruturado** com `Add Log Fields` (TransactionID por log).
- **Screenshots** automáticos de exceções para troubleshooting.
- **Workflows pequenos e reutilizáveis** invocados com argumentos tipados.
