import os
import urllib
import numpy as np
import pandas as pd
from tabula import read_pdf

# 1) Download the source files

# The two source files have different formats. 

# download a csv file called "Puntos_de_Venta.csv" from:
# src_tobac = "https://datos.crtm.es/datasets/ptosventa-logista/data"
# iUnfortunately this has to be done "by hand"

# Download the pharmacies pdf file if it doesn't exist already:
src_pharm = "https://www.comunidad.madrid/sites/default/files/doc/sanidad/orde/oficinas_de_farmacia_abiertas.08062020.pdf"
file_pharm = src_pharm.rsplit('/', 1)[-1]
if not os.path.isfile(file_pharm):
    urllib.request.urlretrieve(src_pharm, file_pharm)

# 2) Read the source files and store the data in pandas dataframes:
df_tobac_raw = pd.read_csv("Puntos_de_Venta.csv")
df_pharm_raw = read_pdf(file_pharm, pages="all")


# 3) Data selection and cleaning.
# Only establishments in Madrid:
df_tobac_madrid_raw = df_tobac_raw[(df_tobac_raw["Municipio"]=="Madrid")]
df_pharm_madrid_raw = df_pharm_raw[(df_pharm_raw["Municipio"]=="Madrid")]

# Only postal code and address are of interest:
df_tobac_madrid = df_tobac_madrid_raw[["Código_Po", "Dirección"]]
df_pharm_madrid = df_pharm_madrid_raw[["CP", "Dirección OF"]]

# Same names for the columns for both dataframes:
df_tobac_madrid.columns = ["CP", "Dirección"]
df_pharm_madrid.columns = ["CP", "Dirección"]

# Remove registers with missing values:
df_tobac_madrid = df_tobac_madrid.dropna(inplace=False)
df_pharm_madrid = df_pharm_madrid.dropna(inplace=False)

# Narrow the search to the center of Madrid, this is, 
# postal code under 28020:
CP_max = 28020
df_tobac_madrid_center = df_tobac_madrid[df_tobac_madrid["CP"].astype(int) < CP_max]
df_pharm_madrid_center = df_pharm_madrid[df_pharm_madrid["CP"].astype(int) < CP_max]

# Export the clean dataframes:
#df_tobac_madrid.to_csv("tobac.csv")
#df_pharm_madrid.to_csv("pharm.csv")

# 
address_tobac = df_tobac_madrid_center["Dirección"]
address_pharm = df_pharm_madrid_center["Dirección"]

# All letters to lowercase:
address_tobac = [str(x).lower() for x in address_tobac]
address_pharm = [str(x).lower() for x in address_pharm]

# More data cleaning:
tabu1 = ["calle", "avenida", "paseo", "plaza", "carretera", "bulevar", "dirección", "nan", ""]
tabu2 = ["cl", "av", "av.", "avda", "avda.", "pl", "ps", "pz", "ctra"]
tabu3 = ["a", "la", "el", "de", "del", "los", "las"]
tabu4 = ["cp", "of", "s//n"]
tabu = tabu1 + tabu2 + tabu3 + tabu4
# remove punctiation signs
# Highlight addresses with weird symbols like 
# interrogation signs (c?rdoba), we might have missed a match. 

address_tobac_clean = []
for tobac in address_tobac:
    resultwords  = [word for word in tobac.replace(",","").split() if word not in tabu]
    result = ' '.join(resultwords)
    address_tobac_clean.append(result)
    
address_pharm_clean = []
for pharm in address_pharm:
    resultwords  = [word for word in pharm.replace(",","").split() if word not in tabu]
    result = ' '.join(resultwords)
    address_pharm_clean.append(result)


# 4) Calculation of which streets meet the criterion:

lista = []

for idx_tobac, tobac in enumerate(address_tobac_clean):
    words_tobac = [p for p in tobac.split() if p.isalpha()]
    nums_tobac = [p for p in tobac.split() if p.isdigit()]
    if len(nums_tobac) >= 1:
        num_tobac = int(nums_tobac[0])
        #num_tobac_par = num_tobac % 2 == 0
    #else:
    #print(idx_tobac, tobac)
    #print(num_tobac)

    for idx_pharm, pharm in enumerate(address_pharm_clean):
        words_pharm = [p for p in pharm.split() if p.isalpha()]
        nums_pharm = [p for p in pharm.split() if p.isdigit()]
        if len(nums_pharm) >= 1:
            num_pharm = int(nums_pharm[0])
            #num_pharm_par = num_pharm % 2 == 0

        if words_tobac != [] and words_pharm != []:
            if (abs(num_tobac-num_pharm) == 2):
                x = all(pf in words_tobac for pf in words_pharm)
                y = all(pe in words_pharm for pe in words_tobac)
                if x and y:
                    lista.append([' '.join(words_tobac), num_pharm])

# 5) Print results:

df = pd.DataFrame(lista, columns=["Street", "Number"])
print(df)
df.to_csv("results.csv", index=False)
