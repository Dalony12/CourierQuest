import pickle
import os
import pprint

#Guarda klos datos binarios del juego

def guardar_en_slot(estado, carpeta="saves/slots"):
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, "slot1.dat")

    # Verificar si el estado es serializable
    try:
        pickle.dumps(estado)
    except Exception as e:
        print(f"[ERROR] No se pudo serializar el estado: {type(e).__name__} - {e}")
        return False

    # Intentar guardar el archivo
    try:
        with open(ruta, "wb") as f:
            pickle.dump(estado, f)
        return True
    except Exception as e:
        print(f"[ERROR] No se pudo guardar el archivo: {type(e).__name__} - {e}")
        return False

#Carga los datos binarios al juego

def cargar_desde_slot(carpeta="saves/slots", nombre_archivo="slot1.dat"):
    ruta = os.path.join(carpeta, nombre_archivo)

    # Verificar si el archivo existe
    if not os.path.exists(ruta):
        print(f"[ERROR] El archivo no existe: {ruta}")
        return None

    # Intentar cargar el estado
    try:
        with open(ruta, "rb") as f:
            estado = pickle.load(f)
        return estado
    except Exception as e:
        print(f"[ERROR] No se pudo cargar el estado: {type(e).__name__} - {e}")
        return None


