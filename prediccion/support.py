import pandas as pd
import numpy as np
from datetime import date, datetime
import pickle

import warnings
warnings.filterwarnings("ignore")

def holiday(col):
    # Creamos una lista con los días festivos
    lista_holiday = ["01-01-2018", "16-01-2018", "20-02-2018", "31-03-2018", 
                    "29-05-2018", "04-07-2018", "05-07-2018", "28-07-2018", 
                    "04-09-2018", "10-11-2018", "23-11-2018", "24-11-2018", 
                    "24-12-2018", "25-12-2018", "31-12-2018", "01-01-2019", 
                    "16-01-2019", "20-02-2019", "31-03-2019", "29-05-2019", 
                    "04-07-2019", "05-07-2019", "28-07-2019", "04-09-2019", 
                    "10-11-2019", "28-11-2019", "29-11-2019", "24-12-2019", 
                    "25-12-2019", "31-12-2019"]
    if col in lista_holiday:
        hol = 1
    else:
        hol = 0
    return hol

# Como las estaciones no coinciden con la fecha, creamos una función para ponerlo bien
def season_of_date(col):
    year= col.year
    seasons = {'spring': pd.date_range(start= '21-03-' + str(year), end= '20-06-' + str(year) ),
               'summer': pd.date_range(start= '21-06-' + str(year), end= '22-09-' + str(year) ),
               'autumn': pd.date_range(start= '23-09-' + str(year), end= '20-12-' + str(year))}
    if col in seasons['spring']:
        return 'spring'
    if col in seasons['summer']:
        return 'summer'
    if col in seasons['autumn']:
        return 'autumn'
    else:
        return 'winter'

def workingday(col1, col2):
    # Le pasamos las columnas holiday y weekday
    if col1 == 1 or col2 == 6 or col2 == 7: 
        # Si holiday es 1 (vacaciones) y weekday es 6 o 7 (sábado o domingo) --> 0
        return 0
    else:
        # Para los demás días --> 1
        return 1

def usuario(fe,cli, dataf):
    meses = {"01":"enero", "02":"febrero", "03":"marzo", 
            "04":"abril", "05": "mayo","06":"junio", 
            "07": "julio", "08": "agosto", "09": "septiembre", 
            "10": "octubre", "11": "noviembre", "12": "diciembre"}
    dict_clima = {"1": "despejado", "2": "nublado", "3": "tormenta", "4":"horrible"}

    dteday = "-".join(fe)+"-2019"

    for k,v in dict_clima.items():
        if v in cli:
            clima = cli.replace(v,k)

    for k,v in meses.items():
        if v in dteday:
            dteday = dteday.replace(v,k)

    dict_usuario = {"dteday" : dteday,"season": 0 , "yr": 1, "mnth":0 ,
                    "holiday": 0, "weekday": 0 ,"workingday":0, "weathersit": int(clima), 
                    "atemp": 0, "hum": 0, "windspeed": 0 }
    df_usuario = pd.DataFrame(dict_usuario, index = [0])

    # Creamos una lista con los días festivos
    lista_holiday = ["01-01-2018", "16-01-2018", "20-02-2018", "31-03-2018", 
                    "29-05-2018", "04-07-2018", "05-07-2018", "28-07-2018", 
                    "04-09-2018", "10-11-2018", "23-11-2018", "24-11-2018", 
                    "24-12-2018", "25-12-2018", "31-12-2018", "01-01-2019", 
                    "16-01-2019", "20-02-2019", "31-03-2019", "29-05-2019", 
                    "04-07-2019", "05-07-2019", "28-07-2019", "04-09-2019", 
                    "10-11-2019", "28-11-2019", "29-11-2019", "24-12-2019", 
                    "25-12-2019", "31-12-2019"]
    
    df_usuario["holiday"] = df_usuario["dteday"].apply(holiday)

     # Cambiamos la columna dteday a datetime
    df_usuario.dteday = pd.to_datetime(df_usuario.dteday)
    # Pasamos la funcion
    df_usuario["season"] = df_usuario["dteday"].apply(season_of_date)
    df_usuario["weekday"] = df_usuario["dteday"].dt.dayofweek
    # Le sumamos uno para que vayan del 1 al 7, de lunes a domingo
    df_usuario["weekday"] = df_usuario["weekday"] + 1
    df_usuario["mnth"] = df_usuario["dteday"].dt.month

    df_usuario["workingday"] = df_usuario.apply(lambda col: workingday(col["holiday"], col["weekday"]), axis = 1)

    season = df_usuario["season"][0]
    weathersit = df_usuario["weathersit"][0]
    month = df_usuario["mnth"][0]
    holiday_yn = df_usuario["holiday"][0]

    humedad = dataf[(dataf["season"] == season) & (dataf["weathersit"] == weathersit) & (dataf["mnth"] == month) &(dataf["holiday"] == holiday_yn)]["hum"].mean()
    sensacion = dataf[(dataf["season"] == season) & (dataf["weathersit"] == weathersit) & (dataf["mnth"] == month) &(dataf["holiday"] == holiday_yn)]["atemp"].mean()
    viento = dataf[(dataf["season"] == season) & (dataf["weathersit"] == weathersit) & (dataf["mnth"] == month) &(dataf["holiday"] == holiday_yn)]["windspeed"].mean()

    df_usuario[["atemp", "hum", "windspeed"]] = sensacion, humedad, viento
    df_usuario.drop("dteday", axis=1, inplace= True)

    return df_usuario
    
def encoding(dataf):
    map_holiday = {0:7, 1:0}
    dataf["holiday"] = dataf["holiday"].map(map_holiday)
    map_weathersit = {3:0, 2:2, 1:4}
    dataf["weathersit"] = dataf["weathersit"].map(map_weathersit)
    map_season = {"winter":0, "autumn":1, "spring":1, "summer":2}
    dataf["season"] = dataf["season"].map(map_season)
    mapa_weekday = {1: 0, 2:1, 3: 1, 4: 2, 5: 2, 6:2, 7:1}
    dataf["weekday"] = dataf["weekday"].map(mapa_weekday)
    mapa_mnth = {1: 0, 2:0, 3: 1, 4: 1, 5: 2, 6:2, 7:2, 8:2, 9:2, 10:2, 11:1, 12:1}
    dataf["mnth"] = dataf["mnth"].map(mapa_mnth)
    map_workingday = {0:1, 1:2}
    dataf["workingday"] = dataf["workingday"].map(map_workingday)
    map_yr = {0:1, 1:2}
    dataf["yr"] = dataf["yr"].map(map_yr)

    return dataf