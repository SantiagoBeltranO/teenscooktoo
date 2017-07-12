# -*- encoding: utf-8 -*-
from models.models import *

def formatunidad(unidad):
    if unidad == 'blank':
        return ""
    else:
        return unidad

def formatquantity(quantity):
    if quantity == 0.0:
        return ""
    elif quantity == 0.5:
        return "1/2"
    elif quantity == 0.25:
        return "1/4"
    elif quantity == 0.75:
        return "3/4"
    elif int(quantity) == quantity:
        return int(quantity)
    else:
        return quantity

def formatcadena(cadena):
    nuevacadena = ""
    for c in cadena:
        nuevacadena += c
        if c == '.':
            nuevacadena += '<br />'
    return nuevacadena

def getcadenanav():
    item = Item()
    menu = item.get_nav()
    # selecciona los menus de nivel 0
    menu0 = []
    for m in menu:
        if m[8] == 0:
            menu0.append(m)

    if len(menu0):
        menu0 = sorted(menu0, key=lambda menu: menu[6])
        lista = ['<ul class="sf-menu">']
        for m0 in menu0:
            lista.append('<li>')
            ancla = '<a href="#" title="' + m0[4] + '">' + m0[3] + '</a>'
            lista.append(ancla)
            # selecciona los menus de nivel 1
            menu1 = []
            for m in menu:
                if m[8] == 1 and m[1] == m0[0]:
                    menu1.append(m)
            if len(menu1):
                menu1 = sorted(menu1, key=lambda menu: menu[6])
                lista.append('<ul>')
                for m1 in menu1:
                    lista.append('<li>')
                    if not m1[2]:
                        ancla = '<a href="#" title="' + m1[4] + '">' + m1[3] + '</a>'
                    else:
                        ancla = '<a class="hoja" title="' + m1[4].encode('utf-8') + '" href="/' + m1[5] + '">' + m1[3] + '</a>'
                    lista.append(ancla)
                    # selecciona los menus de nivel 2
                    menu2 = []
                    for m in menu:
                        if m[8] == 2 and m[1] == m1[0]:
                            menu2.append(m)
                    if len(menu2):
                        menu2 = sorted(menu2, key=lambda menu: menu[6])
                        lista.append('<ul>')
                        for m2 in menu2:
                            lista.append('<li>')
                            if not m2[2]:
                                ancla = '<a href="#" title="' + m2[4] + '">' + m2[3] + '</a>'
                            else:
                                ancla = '<a class="hoja" title="' + m2[4] + '" href="/' + m2[5] + '">' + m2[3] + '</a>'
                            lista.append(ancla)
                            # selecciona los menus de nivel 3
                            menu3 = []
                            for m in menu:
                                if m[8] == 2 and m[1] == m2[0]:
                                    menu3.append(m)
                            if len(menu3):
                                menu3 = sorted(menu3, key=lambda menu: menu[6])
                                lista.append('<ul>')
                                for m3 in menu3:
                                    lista.append('<li>')
                                    if not m3[2]:
                                        ancla = '<a href="#" title="' + m3[4] + '">' + m3[3] + '</a>'
                                    else:
                                        ancla = '<a class="hoja" title="' + m3[4] + '" href="/' + m3[5] + '">' + m3[3] + '</a>'
                                    lista.append(ancla)

                                    lista.append('</li>')

                                lista.append('</ul>')

                            lista.append('</li>')

                        lista.append('</ul>')

                    lista.append('</li>')

                lista.append('</ul>')

            lista.append('</li>')

        lista.append('</ul>')
        cadena = ""
        for l in lista:
            cadena += l.strip()
        return cadena.strip()
    else:
        return ""
