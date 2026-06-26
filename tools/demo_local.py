"""
DEMO LOCAL — simula o pipeline do RPA EmailToACME sem UiPath/Orchestrator/ACME.

Reproduz fielmente:
  - Dispatcher: parse do corpo do e-mail (mesmas regex) + validacao do vendor
                (le AcceptedVendors do Config.xlsx real) -> "enfileira" ou rejeita.
  - Performer : regra de negocio (vendor habilitado) + criacao do Work Item
                (gera um WIID simulado, como o ACME faria).

NAO substitui a execucao no UiPath — serve para VER A LOGICA rodando agora.
"""
import re
import openpyxl
from pathlib import Path

CONFIG = Path(__file__).resolve().parent.parent / "1.Dispatcher" / "Data" / "Config.xlsx"

# Mesmos casos do send_test_emails.py (3 validos + 1 invalido)
TEST_EMAILS = [
    ("New Work Item - fatura 8841", "fornecedor.a@acme.com",
     "Type: WI5\nVendor: ACME Corp\nDescription: Reconciliar fatura 8841 do mes de junho"),
    ("New Work Item - pedido 5520", "vendas@lisper.com",
     "Type: WI4\nVendor: Lisper\nDescription: Validar pedido 5520 e anexar nota"),
    ("New Work Item - contrato", "contratos@saturn.com",
     "Type: WI3\nVendor: Saturn\nDescription: Conferir clausula 12 do contrato"),
    ("New Work Item - INVALIDO", "spam@bradesco.com",
     "Type: WI5\nVendor: Bradesco\nDescription: Vendor nao autorizado"),
]


def load_accepted_vendors():
    wb = openpyxl.load_workbook(CONFIG, read_only=True)
    ws = wb["Settings"]
    for name, value, *_ in ws.iter_rows(min_row=2, values_only=True):
        if name == "AcceptedVendors":
            return [v.strip() for v in str(value).split(";")]
    return []


def parse_body(body: str):
    def grab(label):
        m = re.search(rf"{label}:\s*(.+)", body)
        return m.group(1).strip() if m else ""
    return {"WIType": grab("Type"), "Vendor": grab("Vendor"), "Description": grab("Description")}


def dispatcher(emails, accepted):
    print("=" * 64)
    print("  1) DISPATCHER  — le e-mails, valida e enfileira")
    print("=" * 64)
    queue, enq, rej = [], 0, 0
    for subject, sender, body in emails:
        data = parse_body(body)
        valid = all(data.values()) and data["Vendor"] in accepted
        if valid:
            item = {**data, "EmailFrom": sender, "EmailSubject": subject}
            queue.append(item)
            enq += 1
            print(f"  [ENFILEIRADO] {data['Vendor']:<10} | {data['WIType']} | {subject}")
        else:
            rej += 1
            motivo = "vendor nao aceito" if all(data.values()) else "campos faltando"
            print(f"  [REJEITADO  ] {data['Vendor']:<10} | {motivo:<18} | {subject}")
    print(f"\n  -> Queue 'EmailWorkItems': {enq} item(ns) | Rejeitados: {rej}\n")
    return queue


def create_work_item(item, idx):
    # Simula o ACME gerando o numero do Work Item.
    return f"WI-{1000 + idx}"


def performer(queue, accepted):
    print("=" * 64)
    print("  2) PERFORMER (REFramework) — consome a fila e cria Work Items")
    print("=" * 64)
    ok, biz = 0, 0
    for i, item in enumerate(queue, start=1):
        print(f"\n  --- Transacao #{i}  (ref vendor={item['Vendor']}) ---")
        # Regra de negocio do Process.xaml
        if item["Vendor"] not in accepted:
            biz += 1
            print(f"      BusinessRuleException: vendor nao habilitado -> Failed/Business (sem retry)")
            continue
        wiid = create_work_item(item, i)
        ok += 1
        print(f"      login ACME ... OK")
        print(f"      cria Work Item: tipo={item['WIType']} vendor={item['Vendor']}")
        print(f"      [SUCCESS] Work Item criado: {wiid}  -> Transaction Status = Successful")
    print("\n" + "-" * 64)
    print(f"  RESULTADO: {ok} sucesso(s) | {biz} Business Exception(s)")
    print("-" * 64)


def main():
    accepted = load_accepted_vendors()
    print(f"\nAcceptedVendors (do Config.xlsx): {accepted}\n")
    queue = dispatcher(TEST_EMAILS, accepted)
    performer(queue, accepted)
    print("\nDEMO concluida. (Logica identica a dos .xaml; sem dependencia de UiPath.)\n")


if __name__ == "__main__":
    main()
