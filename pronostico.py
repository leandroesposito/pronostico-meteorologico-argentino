import requests
import re
from datetime import datetime
import pandas as pd

#
# CAMBIAR ID DE LOCALIDAD A TU LOCALIDAD
#
ID_LOCALIDAD = "4864" 
#
#
#

def getToken():
    url = "https://www.smn.gob.ar/"    
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0",
        "Accept": "application/json",
    }

    response = requests.request("GET", url, headers=headers)
    # regex para extraer el token del HTML de la página
    tokenRegex = r"(?P<token>(?<=localStorage.setItem\('token', ')(.*?))'\)"
    token = re.search(tokenRegex, response.text)
    return token.group("token")

def main():
    # url de conexión a la API del servicio meteorológico nacional
    url = "https://ws1.smn.gob.ar/v1/forecast/location/" + ID_LOCALIDAD
    # token necesario para realizar una consulta a la API
    token = getToken()

    headers = {
        "Accept": "application/json",
        "Authorization": f"JWT {token}",
    }

    response = requests.request("GET", url, headers=headers)
    r_json = response.json()

    # invierto los datos con reversed() para imprimir los días mas cercanos último
    # y no tener que scrollear hasta el inicio
    for date_forecast in reversed(r_json["forecast"]):
        date = datetime.strptime(date_forecast["date"], "%Y-%m-%d")

        # muestra una línea separadora con el dia de la semana y la fecha correspondoente a la tabla
        print("\n" * 3, "#" * 40, "\t",date.strftime("%A"), date.strftime("%Y-%m-%d"), "\t", "#" * 40)

        # extrae solo los campos mas importantes para el dia de hoy
        today_forecast = {k: [date_forecast[k]] for k in date_forecast if k in ["temp_min","temp_max","humidity_min","humidity_max"]}

        today_moments = {}
        for moment in ["early_morning", "morning", "afternoon", "night"]:
            # extrae los momentos del dia con datos para no mostrar los momentos vacios ya pasados
            if date_forecast[moment] is not None:
                today_moments[moment] = {k: date_forecast[moment][k] for k in date_forecast[moment] if k in ["temperature","humidity","rain_prob_range","visibility",]}
                today_moments[moment]["weather"] = date_forecast[moment]["weather"]["description"]
                today_moments[moment]["wind"] = date_forecast[moment]["wind"]["direction"]

        # dataframe para mostrar el resumen del dia en formato de tabla
        today_forecast_df = pd.DataFrame(today_forecast)
        print("Pronóstico para el dia completo")
        print(today_forecast_df)

        # dataframe para mostrar los momentos del dia en formato de tabla
        today_moments_df = pd.DataFrame(today_moments)
        print()
        print("Pronostico para la mañana, tarde y noche")
        print(today_moments_df)

    loc = r_json["location"]
    print()
    print(f'{loc["province"]} - {loc["department"]} - {loc["name"]}')
    print()

if __name__ == "__main__":
    main()