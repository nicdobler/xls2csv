import re

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
    '^"(Traspaso):.*"$'
    ]

with open('file.csv') as myFile:
    for line in myFile.readlines():
        matched = False
        for p in patrones:
            if matched:
                break
            x = re.findall(p, line)
            if x:
                print(x[0], " --> ", line.rstrip())
                matched = True
        if not matched:
            print("Not found: ", line.rstrip())
