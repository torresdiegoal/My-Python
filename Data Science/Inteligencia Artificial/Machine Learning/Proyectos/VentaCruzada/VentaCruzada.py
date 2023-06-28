

import os.path
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules
import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings("ignore", category=UserWarning)  # ignora los warnings

# File = "C:/Users/Diego Torres/OneDrive - Manar Technologies SAS/Petcol/BD/DataINVentaCruzada.csv"
inpath = "C:/Users/Diego Torres/OneDrive - Manar Technologies SAS/Documentos compartidos/01_Proyectos/02_Externos/Carvajal/01_ProyectoRFM-Ventacruzada/4. Realización/Insumos/"
outpath = "C:/Users/Diego Torres/OneDrive - Manar Technologies SAS/Documentos compartidos/01_Proyectos/02_Externos/Carvajal/01_ProyectoRFM-Ventacruzada/4. Realización/Venta_Cruzada/"

df_VC_tmp = pd.read_csv(inpath + 'Base_VentaCruzada_CSV.csv', delimiter=';', decimal=",",
                        # usecols=['%Cliente','Fecha', 'Producto'],
                        dtype={'%Cliente': int, 'Fecha': 'string',
                               'Producto': 'string'}
                        )
# df_VC_tmp = df_VC_tmp['Total_Facturada'].astype(str).astype(float)
df_VC_tmp.columns = ['Key', 'IdCliente', 'IdProducto',
                     'Producto', 'Fecha', 'Cantidad', 'Total']
df_VC_tmp["Key"] = pd.to_datetime(
    df_VC_tmp['Fecha'], format="%d/%m/%Y").astype(str) + "|" + df_VC_tmp["IdCliente"].astype(str)

#################
# Descriptivos
print(df_VC_tmp.sample(5))
print(' ')
print('Summary:')
df_VC_tmp.info()
print(' ')
print('Descriptivos:')
print(df_VC_tmp.describe().round(2).transpose())
print(' ')
print('Nulos por campo:')
print(df_VC_tmp.isnull().sum())  # total de nulls por variable
print(' ')
print('Dimensiones:')
print(df_VC_tmp.shape)


""" 
#####################
## Elimina outliers
df_VC = df_VC_tmp # Creamos una copia de la base

def bye_outliers(var):
    # calculo de cuartiles
    Q1 = np.percentile(df_VC[var], 25)
    Q3 = np.percentile(df_VC[var], 75)

    # Distancia intercuartil
    IQR = Q3 - Q1

    # Limite superior
    LS = Q3 + 1.5 * IQR

    # Limite inferior
    LI = Q1 - 1.5 * IQR

    # Atributo
    print('Variable: ' +  str(var))

    # Limite Superior
    print('Limite inferior: ' +  str(LI))

    # Limite inferior
    print('Limite superior: ' +  str(LS))

    # Filtra el dataframe
    return(df_VC[(df_VC[var] < LS) & (df_VC[var] > LI)])
    print('Nuevas dimensiones del dataframe: ', df_VC.shape)

# Quitamos valores atipicos de Total
# df_VC = bye_outliers('Total')
# print('Dataset sin datos atipicos: ',df_VC.shape) 


#################
## Quitar Duplicados
# Validamos duplicados
def deal_duplicates_ventaCruzada(df, unify = True):
    ids = df['IdProducto'].nunique()
    desc = df['Producto'].nunique()
    ### determina si hay duplicados
    if id != desc:
        print(' ')
        print('Buscando duplicados...')
        print('El set de datos contiene duplicados!')
        # Creamos un subset que contenga ambos campos
        par = df[['Producto', 'IdProducto']].drop_duplicates()
        par.to_csv(outpath + 'Descrip.csv')
        ### hay mas descripciones o ids?
        if ids < desc: 
            ## Un id puede tener varias descripciones por errores de ortografia, pueden unificarse...
            ## siempre y cuando asi se determine segun el archivo 'Descrip.csv'  
            # cuando los id tienen mas de 1 descripcion 
            dup = par.groupby('IdProducto').count()[['Producto']] 
            # si no resetea el index, IdProducto pasa a ser el nombre de las filas y se elimina el campo
            dup = dup.reset_index() 
            # tomamos los valores con mas de 1 descripcion
            dup = dup[dup['Producto'] > 1]
            print('Id`s duplicados: ', dup.shape)
        
            ### Si se decide unificar las descripciones duplicadas o quitar          
            if unify == True : ### OPCION A: UNIFICAR DUPLICADOS
                # vamos a elegir un unico elemento por cada Id y asi unificar los duplicados en la transaccional
                par = par[par['IdProducto'].isin(dup['IdProducto'])]
                par = par.sort_values(by = ['IdProducto', 'Producto'], ascending = True ) 
                par_last = par.groupby('IdProducto').last()[['Producto']]
                # llevamos al valor de producto unico por cada ID a la transaccional
                df = df.merge(par_last, how = 'left', 
                       #on = 'IdProducto' 
                       left_on = 'IdProducto', 
                       right_on = 'IdProducto')
                df['Producto'] = df['Producto_y'].fillna(df['Producto_x'])
                df = df.drop(['Producto_x','Producto_y'], axis=1)

            else: ### OPCION B: QUITAR DUPLICADOS
                df = df[~df['IdProducto'].isin(dup['IdProducto'])] 
        if ids > desc: ### Quitar Duplicados
            # cuando las descripciones tienen mas de 1 id 
            dup = par.groupby('Producto').count()[['IdProducto']] 
            # si no reseta el index, IdProducto pasa a ser el nombre de las filas y se elimina el campo
            dup = dup.reset_index() 
            # tomamos los valores con mas de 1 id
            dup = dup[dup['IdProducto'] > 1] 
            print('Descripciones duplicadas: ', dup.shape)
            df = df[~df['Producto'].isin(dup['Producto'])] 

    else:
        print('Resultado: el set de datos no contiene duplicados')
            
    # Actualizamos valores
    ids = df['IdProducto'].nunique()
    desc = df['Producto'].nunique()
    # Validamos duplicados
    print('Dataset sin duplicados 1era revision: ', df.shape)
    print('IdProducto: ', ids)
    print('Producto: ', desc)

    

    # En algunos casos despues de unificar, quedan visibles mas Ids que descripciones, por lo que 
    # # realizamos esta ultima depuracion 
    if ids > desc: ### Quitar Duplicados
        print(' ')
        print('Ahora hay mas Ids que descripciones, hay que quitar estos registros y listo')
        # Creamos un subset que contenga ambos campos
        par = df[['Producto', 'IdProducto']].drop_duplicates()
        # cuando las descripciones tienen mas de 1 id 
        dup = par.groupby('Producto').count()[['IdProducto']] 
        # si no reseta el index, IdProducto pasa a ser el nombre de las filas y se elimina el campo
        dup = dup.reset_index() 
        # tomamos los valores con mas de 1 id
        dup = dup[dup['IdProducto'] > 1] 
        print('Descripciones duplicadas: ', dup.shape)
        df = df[~df['Producto'].isin(dup['Producto'])] 
    
        ids = df['IdProducto'].nunique()
        desc = df['Producto'].nunique()

    if ids == desc:
        print(' ')
        print('Completado, se han removido exitosamente todos los duplicados faltantes')# Validamos duplicados

    print(df.shape)
    print('IdProducto: ', ids)
    print('Producto: ', desc)

    return(df)

df_VC = deal_duplicates_ventaCruzada(df_VC, unify=True) 
#print(df_VC.sample(5))


##################
### MODELADO
# Creamos una funcion que retorna una matriz en formato ONE-HOT (oh), o 
# un campo por cada categoria de uno o varios campos
def matriz(df, id = True): 
    # True si se utilizaran los ids de producto y no las descripciones
    if id == True:                                                                             # salto de linea, sin espacios adelante para que funcione
        return df.groupby(['Key','IdProducto'])['Cantidad'].sum().unstack().fillna(0). \
        applymap(lambda x: 1 if x > 0 else 0) # devolvera escalar por cada variable
    else:
        return df.groupby(['Key','Producto'])['Cantidad'].sum().unstack().fillna(0). \
        applymap(lambda x: 1 if x > 0 else 0) # usamos las descripciones, poco comun
    
basket = matriz(df_VC, id = True)
print('One-hot matrix ', basket.shape)


######### APRIORI #######
#Se aplica el algoritmo Apriori, para aquellos sets de productos cuyo soporte sea >= que min_soporte que sera de 1%, 
#luego se seleccionan las reglas con una confianza mayor al 80%
item_sets = apriori(basket, min_support = 0.01,
                            use_colnames = True,
                            max_len = 4,
                            #low_memory = True,
                            #verbose = 1) # The level of detail printing when the algorithm runs. Either 0, 1 or 2.
                            )
item_sets = item_sets.sort_values(by = 'support', ascending = False)
print(item_sets.shape)
print(item_sets.head())


##############################
#### METRICAS DE ASOCIACION
## SUPPORT indica la frecuencia de compra de ese producto.
## LIFT nos indica que tan interesante es la asociacion de productos, lift > 1 se consideran de interes
## CONFIDENCE = 0.5 indica que en 50% de los casos en que se compro el producto A, el cliente tambien compro B
rules = association_rules(item_sets, metric = "support", min_threshold = 0.01)
print(rules.columns)
#rules = rules[['antecedents','consequents','support', 'confidence', 'lift']]




print('rules shape: ', rules.shape)
print(rules.head()) 



rules.to_csv(outpath + 'Recomendaciones.csv') """
