import json
import os

def guardar_puntaje(meta_ingresos, ingresos, carpeta="data", archivo="puntajes.json"):
    resultado = {
        "meta": meta_ingresos,
        "ingresos": ingresos,
        "exito": ingresos >= meta_ingresos
    }

    # Crear la carpeta si no existe
    os.makedirs(carpeta, exist_ok=True)

    ruta_completa = os.path.join(carpeta, archivo)

    # Cargar datos existentes si el archivo ya existe
    if os.path.exists(ruta_completa):
        with open(ruta_completa, "r") as f:
            datos = json.load(f)
    else:
        datos = []

    datos.append(resultado)
    datos_ordenados = merge_sort_puntajes(datos)

    # Guardar el nuevo resultado
    with open(ruta_completa, "w") as f:
        json.dump(datos_ordenados, f, indent=4)



def merge_sort_puntajes(lista):
    if len(lista) <= 1:
        return lista

    medio = len(lista) // 2
    izquierda = merge_sort_puntajes(lista[:medio])
    derecha = merge_sort_puntajes(lista[medio:])

    return merge(izquierda, derecha)

def merge(izq, der):
    resultado = []
    i = j = 0

    while i < len(izq) and j < len(der):
        if izq[i]["ingresos"] > der[j]["ingresos"]:  # Mayor a menor
            resultado.append(izq[i])
            i += 1
        else:
            resultado.append(der[j])
            j += 1

    resultado.extend(izq[i:])
    resultado.extend(der[j:])
    return resultado