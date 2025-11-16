import pickle
import os
import pprint

# Guarda los datos binarios del juego
def guardar_en_slot(estado, carpeta="saves/slots"):
    # Crear carpeta si no existe
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, "slot1.dat")

    # Verificar que el estado pueda ser serializado con pickle
    try:
        pickle.dumps(estado)
    except Exception as e:
        print(f"[ERROR] No se pudo serializar el estado: {type(e).__name__} - {e}")
        return False

    # Intentar guardar el archivo binario
    try:
        with open(ruta, "wb") as f:
            pickle.dump(estado, f)
        return True
    except Exception as e:
        print(f"[ERROR] No se pudo guardar el archivo: {type(e).__name__} - {e}")
        return False


# Carga los datos binarios al juego
def cargar_desde_slot(carpeta="saves/slots", nombre_archivo="slot1.dat"):
    ruta = os.path.join(carpeta, nombre_archivo)

    # Verificar si el archivo existe antes de cargarlo
    if not os.path.exists(ruta):
        print(f"[ERROR] El archivo no existe: {ruta}")
        return None

    # Intentar cargar el estado guardado
    try:
        with open(ruta, "rb") as f:
            estado = pickle.load(f)
        return estado
    except Exception as e:
        print(f"[ERROR] No se pudo cargar el estado: {type(e).__name__} - {e}")
        return None

