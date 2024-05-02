import streamlit as st
from utils import utils_hackathon as uh
import pandas as pd

st.set_page_config(layout="wide")

st.title("Hello Météo-France , bienvenue sur Climate Viz")
dict_indicateurs = {"T_MAX": "Temperature maximale"}
c1, c2 = st.columns(2)
ctn = c1.expander("Paramètre")
col11, col12 = ctn.columns(2)


fig2 = uh.map_commune("Montpellier", [43.61361315241169], [3.875541887925083])


end_day = False

commune = col11.selectbox(
    "Choississez votre commune", ["Marseille", "Montpellier", "Niort"], index=None
)
if commune:
    c2.plotly_chart(fig2)
scenario = col12.selectbox(
    "Scénario Climatique", ["RCP2.6", "RCP4.5", "RCP8.5"], index=None
)
if scenario:
    df_drias = pd.read_csv(f"data/drias_montpellier_{scenario}_df.csv")
    df_drias["T_Q"] = df_drias["T_Q"] - 273.15

    df_mf = pd.read_csv("data/mf_montpellier.csv")
ind = col11.selectbox(
    "Choississez un indicateur",
    [
        "Température Max",
        "Température Moyenne",
        "Température Min",
        "Température Seuil",
    ],
    index=None,
)
date_perso = col11.checkbox("Date Personnalisée")

# default date
periode_start = "07-01"
periode_end = "10-30"

# selection date
if date_perso:
    exc1 = c1.expander("Sélection Date Personnalisée")
    exc11, exc12 = exc1.columns(2)
    periode_start = exc11.text_input("Date de Départ", "07-01")
    periode_end = exc12.text_input("Date de Fin", "10-30")

dict_indicateurs = {
    "T_MAX": "Temperature maximale",
    "T_MIN": "Température minimale",
    "T_MOYENNE": "Température moyenne",
    "nb_episodes": "Nombre d'épisodes",
}

# Temperature Seuil
if ind == "Température Seuil":
    seuil = col12.number_input(
        "Séléctionner une température seuil (°C)", -10, 45, value=25
    )
    choix_seuil = col12.radio(
        "Choix seuil",
        ["Température Supérieur", "Température Min"],
    )

    dict_indicateurs = {
        "T_MAX": "Temperature maximale",
        "nb_episodes": "Nombre d'épisodes",
        "Nb_jours_max": f"Nombre de jours où la température est > à {seuil} °C ",
    }
    if choix_seuil == "Température Min":
        signe = "-"
        dict_indicateurs[
            "Nb_jours_max"
        ] = f"Nombre de jours où la température est < à {seuil} °C "
    else:
        signe = "+"
        dict_indicateurs[
            "Nb_jours_max"
        ] = f"Nombre de jours où la température est > à {seuil} °C "

    fig = uh.main_indic_nb_jour_consecutif(
        df_mf,
        df_drias,
        "Nb_jours_max",
        seuil,
        periode_start,
        periode_end,
        dict_indicateurs,
        signe,
    )
    st.plotly_chart(fig)

    # Construction indicateurr temp moy, max, min

    ind_dict = {
        "Température Max": "T_MAX",
        "Température Min": "T_MIN",
        "Température Moyenne": "T_MOYENNE",
    }
    ind = ind_dict[ind]

    fig = uh.main_indic_temperature(
        df_mf=df_mf,
        df_drias=df_drias,
        indicateur=ind,
        periode_start=periode_start,
        periode_end=periode_end,
        dict_indicateurs=dict_indicateurs,
    )
    st.plotly_chart(fig)

if commune and scenario and ind:
    # metrique
    metrique1995 = uh.prepa_df_metrique(df_drias, 1995, periode_start, periode_end, 25)
    metrique2020 = uh.prepa_df_metrique(df_drias, 2030, periode_start, periode_end, 25)
    metrique2050 = uh.prepa_df_metrique(df_drias, 2050, periode_start, periode_end, 25)

    container = st.expander("Nb jour supérieur à 25°C", expanded=True)
    col1, col2, col3 = container.columns(3)
    col1.metric("Horizon 1995", metrique1995)
    col2.metric(
        "Horizon 2020",
        metrique2020,
        str(metrique2020 - metrique1995) + " jours supplémentaires",
    )
    col3.metric(
        "Horizon 2050",
        metrique2050,
        str(metrique2050 - metrique1995) + " jours supplémentaires",
    )
