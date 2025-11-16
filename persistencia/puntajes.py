import json
import os

def guardar_puntaje(meta_ingresos, ingresos, carpeta="data", archivo="puntajes.json"):
    # Crear estructura básica del puntaje obtenido
    resultado = {
        "meta": meta_ingresos,
        "ingresos": ingresos,
        "exito": ingresos >= meta_ingresos  # Si cumplió la meta
    }

    # Crear la carpeta donde se guardará el archivo (si no existe)
    os.makedirs(carpeta, exist_ok=True)

    ruta_completa = os.path.join(carpeta, archivo)

    # Cargar puntajes anteriores si el archivo existe
    if os.path.exists(ruta_completa):
        with open(ruta_completa, "r") as f:
            datos = json.load(f)
    else:
        datos = []  # Si no existe, empezamos lista nueva

    # Agregar el nuevo resultado
    datos.append(resultado)

    # Ordenar puntajes de mayor a menor con merge sort
    datos_ordenados = merge_sort_puntajes(datos)

    # Guardar la lista actualizada en JSON
    with open(ruta_completa, "w") as f:
        json.dump(datos_ordenados, f, indent=4)


def merge_sort_puntajes(lista):
    # Caso base de la recursión
    if len(lista) <= 1:
        return lista

    # Dividir lista en dos mitades
    medio = len(lista) // 2
    izquierda = merge_sort_puntajes(lista[:medio])
    derecha = merge_sort_puntajes(lista[medio:])

    # Mezclar resultados ordenados
    return merge(izquierda, derecha)


def merge(izq, der):
    resultado = []
    i = j = 0

    # Comparar y ordenar por ingresos (de mayor a menor)
    while i < len(izq) and j < len(der):
        if izq[i]["ingresos"] > der[j]["ingresos"]:
            resultado.append(izq[i])
            i += 1
        else:
            resultado.append(der[j])
            j += 1

    # Agregar elementos restantes
    resultado.extend(izq[i:])
    resultado.extend(der[j:])
    return resultado