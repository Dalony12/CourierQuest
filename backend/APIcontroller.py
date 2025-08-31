import requests

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