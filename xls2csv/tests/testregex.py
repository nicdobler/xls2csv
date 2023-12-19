import re

patronesPayee = [
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

with open("file.csv") as myFile:
    for line in myFile.readlines():
        matched = False
        for p in patronesConcepto:
            if matched:
                break
            x = re.findall(p, line)
            if x:
                print(x[0], " --> ", line.rstrip())
                matched = True
        if not matched:
            print("Not found: ", line.rstrip())
