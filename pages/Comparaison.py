import streamlit as st
from utils import utils_hackathon as uh
import pandas as pd


st.write("hello")


dict_indicateurs = {"T_MAX": "Temperature maximale"}
c1, c2 = st.columns(2)
error_date = False

ctn = c1.expander("Paramètre")
col11, col12 = ctn.columns(2)


commune = col11.selectbox(
    "Choississez votre commune",
    ["Commune", "Marseille", "Montpellier", "Niort"],
    index=None,
)
scenario = col12.selectbox(
    "Scénario Climatique", ["Scénario", "RCP2.6", "RCP4.5", "RCP8.5"], index=None
)
if scenario:
    df_drias = pd.read_csv(f"data/drias_montpellier_{scenario}_df.csv")
    df_drias["T_Q"] = df_drias["T_Q"] - 273.15
    df_mf = pd.read_csv("data/mf_montpellier.csv")
    df_mf.drop(columns="Unnamed:0", errors="ignore", inplace=True)

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

    fig, df_d, df_m = uh.main_indic_nb_jour_consecutif(
        df_mf,
        df_drias,
        seuil,
        periode_start,
        periode_end,
        dict_indicateurs,
        signe,
    )

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

    fig, df_d, df_m = uh.main_indic_temperature(
        df_mf=df_mf,
        df_drias=df_drias,
        indicateur=ind,
        periode_start=periode_start,
        periode_end=periode_end,
        dict_indicateurs=dict_indicateurs,
    )


uploaded_file = st.file_uploader(
    "Chargez votre fichier CSV avec les données métiers", type=["csv"]
)

if uploaded_file is not None:
    df_metier = pd.read_csv(uploaded_file)
    df_m.rename(columns={ind: "index"}, inplace=True)
    df_d.rename(columns={ind: "index"}, inplace=True)

    df_m = df_m[["Année", "index"]]
    df_d = df_d[["Année", "index"]]

    df95, df30, df50 = uh.main_inspect_csv(df_metier, df_m, df_d)
    image = uh.show_box_plot(df95, df30, df50)
    st.plotly_chart(image)
    # image.show()
    # corr, fig_reg, fig_temp = uh.main_inspect_csv(df_metier, df_m, df_d)
    # st.plotly_chart(fig_temp)


# if ind == "Température Seuil":
#    nb_jour_cons = col12.number_input("Séléctionner un nombre de jour consécutif",1,365)
#    seuil = col12.number_input("Séléctionner une température seuil (°C)", -10, 45)
#    choix_seuil = col12.radio("Choix seuil", ["Température Min", "Température Supérieur"])
#    if choix_seuil == "Température Min":
#        signe = "-"
#    else:
#        signe = "+"
#
#    df = pd.read_csv("data/drias_montpellier_df.csv")
#    df["T_Q"] = df["T_Q"]-273.15
#    df_drias = uh.calc_nb_episode(df, seuil, signe, nb_jour_cons)
#    #mf
#    df_2 = pd.read_csv("data/Serie_tempo_T_montpellier_daily_1959_2024.csv")
#    df_mf = uh.calc_nb_episode(df_2, seuil, signe, nb_jour_cons)
#
#    df_millesime = st.file_uploader("Charger votre fichier CSV")
#    if df_millesime != None:
#        df_millesime = pd.read_csv(df_millesime)
#        df_millesime.drop(columns="Unnamed: 0", inplace=True)
#        corr, fig_reg, fig_temp = uh.main_inspect_csv(df_millesime, df_mf, df_drias)
#        st.plotly_chart(fig_reg)
#        st.plotly_chart(fig_temp)#
