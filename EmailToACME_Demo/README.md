# EmailToACME_Demo — versão runnable (UiPath Studio 26.0)

Projeto **auto-suficiente** que reproduz o pipeline do EmailToACME **rodando no Studio 26.0**,
sem depender de Gmail, Orchestrator ou conta ACME.

Enquanto os projetos `1.Dispatcher` / `2.Performer` são o REFramework "de produção"
(mira Studio 24.10, precisa de fila do Orchestrator + IMAP + ACME), este demo usa só
**activities básicas** (`Assign`, `For Each`, `If`, `Write Line`) e a dependência
`UiPath.System.Activities`, então **abre e roda com F5** em qualquer Studio 26.0+.

## O que ele faz (mesma lógica dos .xaml)

1. **Dispatcher** — lê uma lista de e-mails de teste, faz o parse (`Type`/`Vendor`/`Description`),
   valida o vendor contra a lista de aceitos e **enfileira** ou **rejeita**.
2. **Performer** — consome a fila e **cria os Work Items** (número simulado, como o ACME faria),
   com Business Exception para vendor não habilitado.

## Rodar

Abra `project.json` no UiPath Studio 26.0+ e aperte **F5**. Saída esperada no Output:

```
[ENFILEIRADO] ACME Corp | WI5 | ...
[ENFILEIRADO] Lisper | WI4 | ...
[ENFILEIRADO] Saturn | WI3 | ...
[REJEITADO]   Bradesco | vendor nao aceito | ...
[SUCCESS] Work Item WI-1001 / WI-1002 / WI-1003
RESULTADO: 3 sucesso(s) | 0 Business Exception(s)
```

> Prefere sem UiPath? `python tools/demo_local.py` (na raiz do repo) roda a mesma lógica em Python puro.
