import streamlit as st
from utils import utils_hackathon as uh
import pandas as pd




dict_indicateurs = {"T_MAX" : "Temperature maximale"}
c1, c2 = st.columns(2)
ctn = c1.expander("Paramètre")
col11, col12 = ctn.columns(2)


# commune = col11.selectbox("Choississez votre commune", ["Commune", "Marseille", "Montpellier", "Niort"])
# scenario = col12.selectbox("Scénario Climatique", ["Scénario", "RCP2.6", "RCP4.5" , "RCP8.5"])
# ind = col11.selectbox("Choississez un indicateur", ["Température Max","Température Moyenne",  "Température Min", "Température Seuil"])
# date_perso = col11.checkbox("Date Personnalisée")

# if ind == "Température Seuil":
#     nb_jour_cons = col12.number_input("Séléctionner un nombre de jour consécutif",1,365)
#     seuil = col12.number_input("Séléctionner une température seuil (°C)", -10, 45)
#     choix_seuil = col12.radio("Choix seuil", ["Température Min", "Température Supérieur"])
#     if choix_seuil == "Température Min":
#         signe = "-"
#     else:
#         signe = "+"

#     df = pd.read_csv("data/drias_montpellier_df.csv")
#     df["T_Q"] = df["T_Q"]-273.15
#     df_drias = uh.calc_nb_episode(df, seuil, signe, nb_jour_cons)
#     #mf
#     df_2 = pd.read_csv("data/mf_montpellier.csv")
#     df_mf = uh.calc_nb_episode(df_2, seuil, signe, nb_jour_cons)
if True:
    df_drias = pd.read_csv("data/drias_temp.csv")
    df_mf = pd.read_csv("data/mf_montpellier.csv")
    print(df_drias.head(3))
    print(df_mf.head(3))
    df_millesime = st.file_uploader("Charger votre fichier CSV")
    if df_millesime != None:
        df_millesime = pd.read_csv(df_millesime)
        df_millesime.drop(columns="Unnamed: 0", inplace=True, errors="ignore")
        corr, fig_reg, fig_temp = uh.main_inspect_csv(df_millesime, df_mf, df_drias)
        st.plotly_chart(fig_reg)
        st.plotly_chart(fig_temp)




