import requests
import json
import os
from datetime import datetime
import glob

def get_data_from_api(url: str):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error al obtener datos ({response.status_code}): {url}")
            return None
    except Exception as e:
        print(f"Excepción al llamar {url}: {e}")
        return None


def CollectInformacionMapa():
    #Collect de los datos del mapa
    mapaUrl = "https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io/city/map"

    data = get_data_from_api(mapaUrl)

    if data:
        return data.get("data", {})   # devuelve todo lo del mapa
    return None


def CollectInformacionPedidos():
    #Collect de los datos de los pedidos
    pedidosUrl = "https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io/city/jobs"

    data = get_data_from_api(pedidosUrl)

    if data:
        return data.get("data", {})   # devuelve todo lo del mapa
    return None

def CollectInformacionClima():
    #Collect de los datos del clima
    climaUrl = "https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io/city/weather?city=TigerCity&mode=mode"
    
    data = get_data_from_api(climaUrl)

    if data:
        return data.get("data", {})   # devuelve todo lo del mapa
    return None

def cargar_con_cache(nombre_base: str, funcion_api):
    """
    Carga datos desde API y guarda:
    - Una copia fija en /data/{nombre_base}.json
    - Una copia con fecha/hora en /api_cache/{nombre_base}_YYYY-MM-DD__hora_HH-MM.json
    Si falla la API, carga la última versión con fecha desde /api_cache/
    """
    carpeta_fija = "data"
    carpeta_cache = "api_cache"
    os.makedirs(carpeta_fija, exist_ok=True)
    os.makedirs(carpeta_cache, exist_ok=True)

    fecha = datetime.now().strftime("%Y-%m-%d__hora_%H-%M")
    archivo_con_fecha = os.path.join(carpeta_cache, f"{nombre_base}_{fecha}.json")
    archivo_fijo = os.path.join(carpeta_fija, f"{nombre_base}.json")

    try:
        datos = funcion_api()
        if datos:
            # Guardar versión con fecha
            with open(archivo_con_fecha, 'w', encoding='utf-8') as f:
                json.dump(datos, f, ensure_ascii=False, indent=4)
            # Guardar versión fija
            with open(archivo_fijo, 'w', encoding='utf-8') as f:
                json.dump(datos, f, ensure_ascii=False, indent=4)
            print(f"[INFO] Datos de '{nombre_base}' cargados desde API y guardados en:")
            print(f"       - {archivo_con_fecha}")
            print(f"       - {archivo_fijo}")
            return datos
    except Exception as e:
        print(f"[WARN] Falló la carga desde API de '{nombre_base}': {e}")

    # Buscar la última versión con fecha en /api_cache/
    patron = os.path.join(carpeta_cache, f"{nombre_base}_*.json")
    archivos = glob.glob(patron)
    if archivos:
        archivo_mas_reciente = max(archivos, key=os.path.getmtime)
        try:
            with open(archivo_mas_reciente, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            print(f"[INFO] Datos de '{nombre_base}' cargados desde la última versión cacheada:")
            print(f"       - {archivo_mas_reciente}")
            return datos
        except Exception as e:
            print(f"[ERROR] Falló la carga desde caché: {e}")

    print(f"[ERROR] No se pudo obtener datos de '{nombre_base}' ni desde API ni desde caché")
    return None


