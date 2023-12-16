import re
import sys

patrones = [
    '^"Compra (?:Internet En )?(.*), Tarj.*$', 
    '^"Pago Movil En (.*), Tarj.*$', 
    '^"Transaccion Contactless En (.*), Tarj.*$', 
    '^Transferencia (?:Inmediata )?A Favor De (.*)(?: Concepto: )?(.*)$', 
    '^Bizum A Favor De (.*)(?: Concepto: )?(.*)?,.*$', 
    '^"Transferencia De (.*), (?:Concepto )?(.*)?\.?".*$', 
    '^Bizum De (.*)(?: Concepto )?(.*)?,.*$', 
    '^"Pago Recibo De (.*), Ref.*$', 
    '^"Recibo (.*) Nº.*$', 
    '^(Traspaso): (.*),.*$',
    '^(Traspaso):,.*$',
    '^"(Traspaso): (.*),.*$'
    ]

with open('file.csv') as myFile:
    for l in myFile.readlines():
        matched = False
        for p in patrones:
            x = re.findall(p, l)
            if x:
                print(x[0], " --> ", l.rstrip())
                matched = True
        if not matched:
            print("Not found: ", l.rstrip())
