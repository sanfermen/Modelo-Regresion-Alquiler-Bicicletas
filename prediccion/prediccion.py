import pandas as pd
import numpy as np
from datetime import date, datetime
import pickle

import support as sp

import warnings
warnings.filterwarnings("ignore")

fecha = input("De qué fecha quiere la predicción? Por ejemplo, 04-junio: ").lower().split("-")

clima = input("Qué tipo de clima hará? Elige entre despejado, nublado y tormenta: ").lower()

df = pd.read_csv("../datos/02-bikes_limpio.csv", index_col= 0)

df_us = sp.usuario(fecha,clima,df)
df_us_encoding = sp.encoding(df_us)

with open ("../datos/estandarizar.pkl" , "rb") as fp:
        bike = pickle.load(fp)

numericas = df_us_encoding[["atemp", "hum", "windspeed"]]
df_bike = pd.DataFrame(bike.transform(numericas))

df_us_encoding[["atemp", "hum", "windspeed"]] = df_bike

with open ("../datos/model_prediccion.pkl" , "rb") as fs:
    modelo = pickle.load(fs)

model = modelo.predict(df_us_encoding)

alquiler = round(model[0])
print(f"El alquiler aproximado de bicicletas para el {fecha[0]} de {fecha[1]}  es de {alquiler} bicicletas")