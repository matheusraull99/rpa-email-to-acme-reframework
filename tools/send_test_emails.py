"""
Dispara e-mails de teste para a caixa monitorada pelo Dispatcher.

Uso (Gmail com App Password — conta de teste com 2FA):
    set RPA_SMTP_USER=rpa.portfolio.teste@gmail.com
    set RPA_SMTP_PASS=xxxx xxxx xxxx xxxx        # App Password (16 chars)
    set RPA_MAIL_TO=rpa.portfolio.teste@gmail.com
    python send_test_emails.py

Gera 3 e-mails validos (vendors aceitos) + 1 invalido (vendor recusado),
no formato que o Dispatcher faz parse (Type:/Vendor:/Description:).
"""
import os
import smtplib
import sys
from email.mime.text import MIMEText

SMTP_HOST = os.getenv("RPA_SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("RPA_SMTP_PORT", "587"))
SMTP_USER = os.getenv("RPA_SMTP_USER")
SMTP_PASS = os.getenv("RPA_SMTP_PASS")
MAIL_TO = os.getenv("RPA_MAIL_TO", SMTP_USER)

# (assunto, tipo, vendor, descricao) — ultimo e invalido de proposito
TEST_CASES = [
    ("New Work Item - fatura 8841", "WI5", "ACME Corp", "Reconciliar fatura 8841 do mes de junho"),
    ("New Work Item - pedido 5520", "WI4", "Lisper",    "Validar pedido 5520 e anexar nota"),
    ("New Work Item - contrato G7",  "WI3", "Saturn",    "Conferir clausula 12 do contrato"),
    ("New Work Item - INVALIDO",     "WI5", "Bradesco",  "Vendor nao autorizado - deve ser rejeitado"),
]


def build_body(wi_type: str, vendor: str, description: str) -> str:
    return f"Type: {wi_type}\nVendor: {vendor}\nDescription: {description}\n"


def main() -> int:
    if not SMTP_USER or not SMTP_PASS:
        print("ERRO: defina RPA_SMTP_USER e RPA_SMTP_PASS (App Password).", file=sys.stderr)
        return 1

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        for subject, wi_type, vendor, desc in TEST_CASES:
            msg = MIMEText(build_body(wi_type, vendor, desc), _charset="utf-8")
            msg["Subject"] = subject
            msg["From"] = SMTP_USER
            msg["To"] = MAIL_TO
            server.send_message(msg)
            print(f"  enviado -> {subject}  (vendor={vendor})")

    print(f"\nOK: {len(TEST_CASES)} e-mails enviados para {MAIL_TO}.")
    print("Rode o Dispatcher para enfileirar; 3 devem ir para a Queue e 1 para Rejected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
