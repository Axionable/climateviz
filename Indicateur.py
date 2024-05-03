import streamlit as st
from utils import utils_hackathon as uh
import pandas as pd


st.set_page_config(layout="wide")

st.title("Hello Météo-France, bienvenue sur Climate Viz")
dict_indicateurs = {"T_MAX": "Temperature maximale"}
c1, c2 = st.columns(2)
ctn = c1.expander("Paramètre")
col11, col12 = ctn.columns(2)
error_date = False
# definition des parametres initaux
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
        "Température de jours qui dépassent une température seuil",
    ],
    index=None,
)
date_perso = col11.checkbox("Date Personnalisée")

# default date
periode_start = "01-01"
periode_end = "12-31"

# selection date
if date_perso:
    exc1 = c1.expander("Sélection Date Personnalisée")
    exc11, exc12 = exc1.columns(2)
    periode_start = exc11.text_input("Date de Départ", "01-01")
    periode_end = exc12.text_input("Date de Fin", "12-31")
    if periode_start and periode_end:
        if not (uh.validate_date(periode_start) and uh.validate_date(periode_end)):
            st.error("Date invalide, entrez une date au format MM-JJ")
            error_date = True
        else:
            error_date = False

dict_indicateurs = {
    "T_MAX": "Temperature maximale",
    "T_MIN": "Température minimale",
    "T_MOYENNE": "Température moyenne",
    "nb_episodes": "Nombre d'épisodes",
}

# Temperature Seuil
if (
    ind == "Température de jours qui dépassent une température seuil"
    and scenario
    and commune
    and not error_date
):
    seuil = col12.number_input(
        "Séléctionner une température seuil (°C)", -10, 45, value=25
    )
    choix_seuil = col12.radio(
        "Choix seuil",
        ["Température Supérieur", "Température Min"],
    )
    dict_indicateurs["Nb_jours_max"] = (
        f"Nombre de jours où la température est > à {seuil} °C ",
    )
    if choix_seuil == "Température Min":
        signe = "-"
        text = f"Nombre de jours qui sous en-dessous  d'une température de {seuil} °C "

    else:
        signe = "+"
        text = f"Nombre de jours qui dépassent une température de {seuil} °C "

    dict_indicateurs["Nb_jours_max"] = text

    fig, df = uh.main_indic_nb_jour_consecutif(
        df_mf,
        df_drias,
        seuil,
        periode_start,
        periode_end,
        dict_indicateurs,
        signe,
    )
    st.plotly_chart(fig)
    ind = "Nb_jours_max"
    metrique_sup = " jours"

# Construction indicateurr temp moy, max, min
if (
    ind in ["Température Max", "Température Moyenne", "Température Min"]
    and scenario
    and commune
    and not error_date
):
    ind_dict = {
        "Température Max": "T_MAX",
        "Température Min": "T_MIN",
        "Température Moyenne": "T_MOYENNE",
    }
    ind = ind_dict[ind]

    fig, df = uh.main_indic_temperature(
        df_mf=df_mf,
        df_drias=df_drias,
        indicateur=ind,
        periode_start=periode_start,
        periode_end=periode_end,
        dict_indicateurs=dict_indicateurs,
    )
    metrique_sup = "° C"
    st.plotly_chart(fig)

if commune and scenario and ind and not error_date:
    # metrique
    metrique2000 = uh.prepa_df_metrique(df, 2000, ind)
    metrique2020 = uh.prepa_df_metrique(df, 2030, ind)
    metrique2050 = uh.prepa_df_metrique(df, 2050, ind)

    container = st.expander(
        "Analyse par horizon du " + dict_indicateurs[ind].lower(), expanded=True
    )
    col1, col2, col3 = container.columns(3)
    col1.metric("Horizon 1995", metrique1995)
    col2.metric(
        "Horizon 2020",
        metrique2020,
        str(metrique2020 - metrique1995) + metrique_sup,
    )
    col3.metric(
        "Horizon 2050",
        metrique2050,
        str(metrique2050 - metrique1995) + metrique_sup,
    )
