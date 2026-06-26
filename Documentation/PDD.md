# PDD — Process Definition Document (resumido)

## 1. Identificação
- **Processo:** Lançamento de Work Items recebidos por e-mail no ACME System 1
- **Tipo:** Atendido? Não — **não atendido** (unattended), agendável via Orchestrator
- **Autor:** Matheus Raul — projeto de portfólio
- **Sistemas:** Caixa de e-mail (Gmail/Outlook), ACME System 1 (web)

## 2. Objetivo
Eliminar a digitação manual de Work Items que chegam por e-mail, reduzindo erro e
tempo de processamento, com rastreabilidade total via Orchestrator Queue.

## 3. Gatilho e frequência
- **Dispatcher:** agendado (ex. a cada 30 min) — coleta e-mails novos.
- **Performer:** agendado logo após, ou em paralelo, consumindo a fila.

## 4. Fluxo AS-IS (manual)
1. Operador abre o e-mail.
2. Lê Tipo, Fornecedor e Descrição.
3. Loga no ACME, cria o Work Item, copia os dados.
4. Marca o e-mail como tratado.

## 5. Fluxo TO-BE (automatizado)
- **Dispatcher**: lê e-mails não lidos → valida → enfileira (1 e-mail = 1 Queue Item)
  → marca e-mail como lido / move para `Processed`.
- **Performer (REFramework)**:
  - `Init`: lê Config, abre o ACME, faz login.
  - `Get Transaction`: pega o próximo item da fila.
  - `Process`: cria o Work Item no ACME e confirma o número gerado.
  - `Set Status`: Success / Business Exception / System Exception (+ retry).
  - `End`: fecha aplicações.

## 6. Exceções
| Situação | Categoria | Ação |
|----------|-----------|------|
| Vendor não autorizado | Business Rule Exception | marca item como Failed/Business, **sem retry**, segue |
| Campo obrigatório vazio | (barrado no Dispatcher) | item nem chega ao Performer |
| ACME fora do ar / timeout | System Exception | retry (até `MaxRetryNumber`), screenshot, reinicia apps |
| Selector não encontrado | System Exception | idem acima |

## 7. Volume e SLA (premissas de portfólio)
- ~50–200 e-mails/dia.
- SLA por item: < 60s.

## 8. Critérios de sucesso
- 0 itens perdidos (garantido pela Queue).
- Itens falhados reprocessáveis sem intervenção manual no dado.
- Logs com `TransactionID` permitindo auditoria item a item.
