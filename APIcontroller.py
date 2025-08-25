import requests

def CollectInformacionAPI():
    #Collect de los datos del mapa
    mapaUrl = "https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io/city/map"

    response = requests.get(mapaUrl)

    if response.status_code == 200:
        data = response.json()
        data = data["data"]
        nombreCiudad = data["city_name"]
        ancho = data["width"]
        largo = data["height"]
        meta = data["goal"]
        tiempoMaximo = data["max_time"]
        celdas = data["tiles"]
        descripcionCeldas = data["legend"] 
    else: print("Error al obtener el mapa:", response.status_code)

    #Collect de los datos de los pedidos
    pedidosUrl = "https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io/city/jobs"

    response = requests.get(pedidosUrl)

    if response.status_code == 200:
        #Agregar las variables de los pedidos
        print()
    else: print("Error al obtener el mapa:", response.status_code)

    #Collect de los datos del clima
    climaUrl = "https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io/city/weather?city=TigerCity&mode=mode"

    data = requests.get(climaUrl)

    if data.status_code == 200:
        #Agregar las variables del clima
        print()
    else: print("Error al obtener el mapa:", response.status_code)