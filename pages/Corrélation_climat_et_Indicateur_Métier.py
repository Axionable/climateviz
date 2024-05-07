import streamlit as st
from utils import utils_hackathon as uh
import pandas as pd

st.set_page_config(page_title="ClimateViz by Axionable - Espace de démo", layout="wide")

st.title("ClimateViz by Axionable - Espace de démo")

c = st.expander("A propos de cet outil")
st.write("""  

Vous souhaitez mesurer l’impact du climat (et donc du changement climatique) sur votre activité ? Mesurer la corrélation entre l’indicateur climatique de votre choix et un indicateur métier de votre choix, et obtenez une première estimation de l’impact du changement climatique sur votre activité.

""")
#Cette page a pour objectif d'apporter une visualisation des prévisions d'une variable métier spécifique sur le long terme à l'aide d'un indicateur climatique choisi. 
#
#Vous avez la possibilité de personnaliser l'indicateur climatique sur lequel vous souhaitez baser vos prévisions en sélectionnant le type de scénario climatique ainsi que la fenêtre temporelle. 
#
#Pour utiliser notre outil de prévision, veuillez fournir un fichier CSV contenant des données historiques sur la variable métier. Ce fichier doit comporter une colonne contenant les valeurs de la variable métier ainsi qu'un historique précis sur une plage temporelle donnée (de l'année X à l'année Y) avec une fréquence annuelle.
#
#Nos prévisions sont calculées grâce à l'utilisation conjointe des données climatiques de Météo France et de DRIAS, ainsi que de l'indicateur choisi, en utilisant des modèles de machine learning.
#
#Explorez les différentes options disponibles et obtenez des prévisions personnalisées pour prendre des décisions éclairées dans votre domaine d'activité.
#""")


#- **Objectif de l'outil** : L'outil permet aux utilisateurs d'évaluer les risque physiques associés à différents actifs en analysant leurs vulnérabilités et expositions aux aléas climatiques
#- **Comment ça fonctionne** : Les utilisateurs chargent un fichier excel sur les actifs analysés qui inclut :
#    - la valeur monétaire
#    - l'exposition aux aléas climatiques selon plusieurs scénarios climatiques et horizons temporels
#    - la vulnérabilité des sites  
#
#L'exposition et la vulnérabilité permet de déterminer un score d'exposition à un risque physique entre faible et élevé. Les actifs avec un score élevés sont considérés comme à risques.  
#           
#- **Données utilisées**: Les analyses sont basées sur une combinaison d'analyse métier (vulnérabilité des sites et valeurs monétaires) et d'indicateurs climatiques (exposition).



dict_indicateurs = {"T_MAX": "Temperature maximale"}
c1, c2 = st.columns(2)
error_date = False

ctn = c1.expander("Mon indicateur climatique à corréler")
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
    ind = "Nb_jours_max"
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



col1, col2 = st.columns(2)

with col1:
    nom_var_metier = st.text_input("Nom indicateur métier")

with col2:
    unite_var_metier = st.text_input("Unité de mesure")


col3, col4 = st.columns(2)
with col3 :
    uploaded_file = st.file_uploader(
        "Déposez un fichier CSV avec votre indicateur métier à corréler", type=["csv"]
    )

with col4: 
    st.write("\n")
    st.write("Le fichier CSV doit comporter une colonne contenant les valeurs de l'indicateur métier ainsi qu'un historique précis sur une plage temporelle donnée (de l'année X à l'année Y) avec une fréquence annuelle.")
    csv_download_link = st.download_button(
    label="Télécharger un exemple",
    data=uh.download_csv(),
    file_name='qualite_vin.csv',
    mime='text/csv'
    )

if uploaded_file is not None:
    df_metier = pd.read_csv(uploaded_file)
    try:
        df_m.rename(columns={ind: "index"}, inplace=True)
        df_d.rename(columns={ind: "index"}, inplace=True)
    except:
        st.warning('Veuillez sélectionner un indicateur')

    df_m = df_m[["Année", "index"]]
    df_d = df_d[["Année", "index"]]

    print(df_metier.head(1))
    print(df_m.head(1))


    col_graphique, col_description = st.columns([2, 1])
    
    with col_graphique:
        image1 = uh.show_serie_tempo(df_metier, df_m, nom_var_metier, " °C", "Note", dict_indicateurs[ind])
        st.plotly_chart(image1)

    nom_var_metier = nom_var_metier.lower()
    df95, df30, df50 = uh.main_inspect_csv(df_metier, df_m, df_d)
    if "jours" in dict_indicateurs[ind]:
        nom_indi_mf = "du " + dict_indicateurs[ind]
    else:
        nom_indi_mf = "de la " + dict_indicateurs[ind]

    with col_description:
        st.write("Information sur le graphique :")
        st.write(f"Ce graphique représente une visualisation de l'évolution de {nom_var_metier} et {nom_indi_mf.lower()} en fonction des années")
    st.markdown("---")
    col_graphique, col_description = st.columns([2, 1])

    with col_graphique:
        image = uh.show_box_plot(df95, df30, df50, scenario, nom_var_metier, unite_var_metier)
        st.plotly_chart(image)

    with col_description:
        st.write("Information sur le graphique :")
        st.write(f"Ce graphique représente une visualisation des prévisions de la {nom_var_metier} pour trois horizons générés à partir d'un modèle de machine learning (un arbre de décision) qui se base sur l'indicateur climatique selectionné.")
        st.write(f"Cette représentation permet de visualiser les variations de la {nom_var_metier} en fonction du scénario climatique {scenario} et de mieux comprendre son impact potentiel sur cette variable spécifique.")

    
c = st.expander("A propos de ce site")

c.markdown(uh.text_explication_fin)


