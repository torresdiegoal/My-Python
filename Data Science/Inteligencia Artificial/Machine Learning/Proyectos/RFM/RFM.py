
# Carga paquetes
import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings("ignore", category=UserWarning)  # ignora los warnings

# Carga de la base
inpath = "C:/Users/Diego Torres/OneDrive - Manar Technologies SAS/Carvajal/Bases/"

BD_ini = pd.read_excel(inpath + 'BD_Carvajal1.xlsx',
                       sheet_name="Hoja2")

#################
# Descriptivos
print(BD_ini.sample(5))
print(' ')
print('Summary:')
BD_ini.info()
print(' ')
print('Descriptivos:')
print(BD_ini.describe().round(2).transpose())
print(' ')
print('Nulos por campo:')
print(BD_ini.isnull().sum())  # total de nulls por variable
print(' ')
print('Dimensiones:')
print(BD_ini.shape)
