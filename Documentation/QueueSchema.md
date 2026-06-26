# Contrato da Queue `EmailWorkItems`

O Dispatcher grava e o Performer lê **exatamente** estes campos. Manter este
contrato estável é o que desacopla os dois robôs.

## Specific Content (campos do Queue Item)

| Chave (key)      | Tipo    | Origem (e-mail)            | Uso no Performer                       |
|------------------|---------|----------------------------|----------------------------------------|
| `WIType`         | String  | corpo: `Type:`             | tipo do Work Item no ACME (WI5/WI4...)  |
| `Description`    | String  | corpo: `Description:`      | descrição do Work Item                  |
| `Vendor`         | String  | corpo: `Vendor:`           | fornecedor (validação de negócio)       |
| `EmailFrom`      | String  | remetente                  | auditoria / rastreabilidade             |
| `EmailSubject`   | String  | assunto                    | auditoria                               |
| `ReceivedAt`     | DateTime| data do e-mail             | SLA                                     |

## Reference

`Reference` do Queue Item = **MessageId** do e-mail (ou hash do assunto+data).
Garante **idempotência**: o Orchestrator pode ser configurado para recusar
duplicados (`Enforce unique references = Yes`), evitando enfileirar o mesmo
e-mail duas vezes.

## Regras de validação (no Dispatcher, antes de enfileirar)

1. `WIType`, `Description` e `Vendor` não podem ser vazios.
2. `Vendor` deve estar na lista de fornecedores aceitos (`Config!AcceptedVendors`).
3. E-mail sem os campos obrigatórios → **não enfileira**, marca com categoria
   `Invalid` e move para a pasta `Processed/Rejected` (não vira Business Exception
   no Performer — falha de dado é barrada na entrada).

## Exemplo de corpo de e-mail processável

```
Type: WI5
Vendor: ACME Corp
Description: Reconciliar fatura 8841 do mes de junho
```
