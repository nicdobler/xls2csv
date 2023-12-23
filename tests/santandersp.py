# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab
# pylint: disable=invalid-name
"""
csv2ofx.mappings.santanderaccount
~~~~~~~~~~~~~~~~~~~~~~~~

Provides a mapping for transactions obtained via Santander Spain Account
(Spanish bank)
"""
from operator import itemgetter
import json
import hashlib
import re


def find_type(transaction):
    amount = float(transaction.get("IMPORTE EUR"))
    return "credit" if amount > 0 else "debit"


def gen_transaction_id(transaction):
    hasher = hashlib.sha256()
    stringified = json.dumps(transaction).encode("utf-8")
    hasher.update(stringified)
    return hasher.hexdigest()


def get_payee(transaction):
    concepto = transaction.get('CONCEPTO')
    patrones = [
        '^"Compra (?:Internet En )?(.*), Tarj.*$',
        '^"Pago Movil En (.*), Tarj.*$',
        '^"Transaccion Contactless En (.*), Tarj.*$',
        '^"Transferencia (?:Inmediata )?A Favor De (.*) Concepto: .*"$',
        '^"Transferencia (?:Inmediata )?A Favor De (.*)"$',
        '^"Bizum A Favor De (.*)(?: Concepto: ).*"$',
        '^"Transferencia De (.*), (?:Concepto .*)?\\.?".*$',
        '^"Bizum De (.*)(?: Concepto ).*?"$',
        '^"Pago Recibo De (.*), Ref.*$',
        '^"Recibo (.*) Nº.*$',
        '^"(Traspaso):.*"$',
    ]
    payee = concepto
    for p in patrones:
        x = re.findall(p, concepto)
        if x:
            payee = x[0]
            break
    return payee


def get_transaction_type(transaction):
    concepto = transaction.get('CONCEPTO')
    patronesConcepto = [
        r'^"Compra (?:Internet En )?.*, (Tarj\. :.*)$',
        r'^"Compra (?:Internet En )?.*, (Tarjeta \d*).*$',
        r'^"Pago Movil En .*, (Tarj\. :.*)$',
        r'^"Transaccion Contactless En .*, (Tarj\. :.*)$',
        r'^"Transferencia (?:Inmediata )?A Favor De .* Concepto: (.*)"$',
        r'^"Bizum A Favor De .* Concepto: (.*)"$',
        r'^"Transferencia De .*, Concepto (.*)\.?"$',
        r'^"Bizum De .* Concepto (.*)"$',
        r'^"Traspaso: (.*)"$',
    ]
    notes = ""
    for p in patronesConcepto:
        x = re.findall(p, concepto)
        if x:
            notes = x[0]
            break
    return notes


mapping = {
    "has_header": True,
    "is_split": False,
    "bank": "Santander",
    "currency": "EUR",
    "delimiter": ",",
    "dayfirst": True,
    "account": itemgetter("Account"),
    "type": find_type,
    "date": itemgetter("FECHA VALOR"),
    "amount": itemgetter("IMPORTE EUR"),
    "payee": get_payee,
    'desc': get_transaction_type,
    "class": itemgetter("class"),
    "id": gen_transaction_id,
}
