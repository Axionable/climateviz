import plotly.express as px
import pandas as pd
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go
from datetime import datetime
from sklearn.tree import DecisionTreeClassifier


def map_commune(commune, latitude, longitude):
    data = {"Latitude": latitude, "Longitude": longitude}

    # Plot the point on the map
    fig = px.scatter_mapbox(data, lat="Latitude", lon="Longitude", zoom=10)

    # Customize map layout
    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_zoom=10,
        mapbox_center={"lat": latitude[0], "lon": longitude[0]},
        title=commune,
        width=300,
    )

    # Show the plot
    return fig


def filtre_temporel_periode(df, date_debut, date_fin):
    df["DATE"] = pd.to_datetime(df["DATE"])

    date_debut = pd.to_datetime(date_debut, format="%m-%d")
    date_fin = pd.to_datetime(date_fin, format="%m-%d")
    df["Mois-Jour"] = df["DATE"].dt.strftime("%m-%d")
    df_filtre = df[
        (df["Mois-Jour"] >= date_debut.strftime("%m-%d"))
        & (df["Mois-Jour"] <= date_fin.strftime("%m-%d"))
    ]
    df_filtre = df_filtre.drop("Mois-Jour", axis=1)
    return df_filtre


def calc_nb_j(df, seuil, signe):
    cpt = 0
    df["DATE"] = pd.to_datetime(df["DATE"])
    resultats = []

    for annee in df["DATE"].dt.year.unique():
        donnees_annee = df[df["DATE"].dt.year == annee]
        if signe == "+":
            cpt = donnees_annee[donnees_annee["T_Q"] >= seuil].shape[0]

        elif signe == "-":
            cpt = donnees_annee[donnees_annee["T_Q"] <= seuil].shape[0]

        else:
            print("Signe non reconnu, veuillez choisir entre '+' et '-' ")

        resultats.append({"Année": annee, "Nb_jours_max": cpt})

    df_final = pd.DataFrame(resultats)

    return df_final


def calc_nb_episode(df, seuil, signe, nb_j_min):
    df["DATE"] = pd.to_datetime(df["DATE"])
    resultats = []

    for annee in df["DATE"].dt.year.unique():
        nb_fois_condition_true = 0
        donnees_annee = df[df["DATE"].dt.year == annee]
        if signe == "+":
            donnees_annee["Condition_Respectee"] = donnees_annee.apply(
                lambda row: row["T_Q"] >= seuil, axis=1
            )

        elif signe == "-":
            donnees_annee["Condition_Respectee"] = donnees_annee.apply(
                lambda row: row["T_Q"] <= seuil, axis=1
            )

        else:
            print("Signe non reconnu, veuillez choisir entre '+' et '-' ")

        donnees_annee.reset_index(drop=True, inplace=True)
        condition_true_consecutifs = (
            donnees_annee["Condition_Respectee"]
            .rolling(window=nb_j_min)
            .apply(lambda x: x.all())
            .fillna(False)
        )
        nb_fois_condition_true = (condition_true_consecutifs.diff() == True).sum()

        resultats.append({"Année": annee, "nb_episodes": nb_fois_condition_true})

    df_final = pd.DataFrame(resultats)

    return df_final


def plot_climate_strip(
    df,
    df_drias,
    indicateur,
    periode_start,
    periode_end,
    dict_indicateurs,
    moy_ref,
    start_year_ref,
    end_year_ref,
):
    fig = go.Figure()
    fig.add_bar(
        x=df["Année"],
        y=df["ANOM_" + indicateur],
        name=f"{dict_indicateurs[indicateur]}",
        marker=dict(color=df[indicateur], coloraxis="coloraxis"),
    )

    if indicateur == "Nb_jours_max":
        hovertemplate = "Année: %{{x}}<br>Anomalie: %{{y:.0f}} jours <br>{}: %{{customdata:.0f}}".format(
            dict_indicateurs[indicateur]
        )
        title = f"{dict_indicateurs[indicateur]} entre le {periode_start} et le {periode_end}.<br>Écart à la moyenne de référence {start_year_ref} à {end_year_ref}. Valeur de référence : {int(moy_ref)} jours"

    else:
        hovertemplate = "Année: %{{x}}<br>Anomalie: %{{y:.0f}} jours <br>{}: %{{customdata:.0f}} °C".format(
            dict_indicateurs[indicateur]
        )
        title = f"{dict_indicateurs[indicateur]} entre le {periode_start} et le {periode_end}.<br>Écart à la moyenne de référence {start_year_ref} à {end_year_ref}. Valeur de référence : {int(moy_ref)} °C"

    fig.update_traces(
        hovertemplate=hovertemplate,
        customdata=df[indicateur],
    )

    fig.update_layout(coloraxis=dict(colorscale="RdYlBu_r"), width=1000)

    fig.update_layout(
        title=title,
        xaxis_title="Année",
    )
    if indicateur == "Nb_jours_max":
        fig.update_yaxes(
            title_text="Anomalie (Nombre de jours)",
            ticktext=[f"Moyenne: {moy_ref:.0f} "],
        )
    else:
        fig.update_yaxes(
            title_text="Anomalie (°C)", ticktext=[f"Moyenne: {moy_ref:.1f} "]
        )

    fig2 = px.line(
        df_drias,
        x="Année",
        y="rolling_avg",
        labels={"rolling_avg": "Écart à la moyenne (°C)", "Année": "Année"},
        color_discrete_sequence=["green"],
        title=f"{dict_indicateurs[indicateur]} entre le {periode_start} et le {periode_end}.<br>Écart à la moyenne de référence {start_year_ref}-{end_year_ref+30}",
    )
    fig2.update_traces(showlegend=False)
    fig2.add_scatter(
        x=df_drias["Année"],
        y=df_drias["avg + std"],
        mode="lines",
        line=dict(width=0),
        fill="tonexty",
        fillcolor="rgba(204, 204, 204, 0.2)",
    )
    fig2.add_scatter(
        x=df_drias["Année"],
        y=df_drias["avg - std"],
        mode="lines",
        line=dict(width=0),
        fill="tonexty",
        fillcolor="rgba(204, 204, 204, 0.2)",
    )

    if indicateur in df_drias:
        for data in fig2.data:
            if indicateur == "Nb_jours_max":
                # on n'affiche pas les dégrés
                data.hovertemplate = "Année: %{{x}}<br>Anomalie: %{{y:.0f}} jours <br>{}: %{{customdata:.0f}}".format(
                    dict_indicateurs[indicateur]
                )
            else:
                data.hovertemplate = "Année: %{{x}}<br>Anomalie: %{{y:.1f}}°<br>{}: %{{customdata:.1f}}°".format(
                    dict_indicateurs[indicateur]
                )
            data.customdata = df_drias[indicateur]

    fig2.update_layout(coloraxis=dict(colorscale="RdYlBu_r"))

    for data in fig2.data:
        data.showlegend = False
        fig.add_trace(data)

    return fig


def temp_max(df):
    df["Année"] = df["DATE"].dt.year
    result = df.groupby(["Année"])["T_Q"].max().reset_index()
    result.rename(columns={"T_Q": "T_MAX"}, inplace=True)
    return result


def temp_min(df):
    df["Année"] = df["DATE"].dt.year
    result = df.groupby(["Année"])["T_Q"].min().reset_index()
    result.rename(columns={"T_Q": "T_MIN"}, inplace=True)
    return result


def temp_moyenne(df):
    df["Année"] = df["DATE"].dt.year
    result = df.groupby(["Année"])["T_Q"].mean().reset_index()
    result.rename(columns={"T_Q": "T_MOYENNE"}, inplace=True)
    return result


def main_indic_temperature(
    df_mf,
    df_drias,
    indicateur,
    periode_start,
    periode_end,
    dict_indicateurs,
):
    if indicateur == "T_MAX":
        temp_function = temp_max
    elif indicateur == "T_MIN":
        temp_function = temp_min
    elif indicateur == "T_MOYENNE":
        temp_function = temp_moyenne

    # filtre temporel
    df_mf_filtre = filtre_temporel_periode(df_mf, periode_start, periode_end)
    df_drias_filtre = filtre_temporel_periode(df_drias, periode_start, periode_end)

    # filtre  et calcul température minimale par année sur MF
    df_mf_temp_min = temp_function(df_mf_filtre)
    val_ref = calcul_val_reference(df_mf_temp_min, indicateur)
    df_mf_temp_min = calcule_anomalie(df_mf_temp_min, indicateur, val_ref)

    # fitlre et calcul sur DRIAS
    df_drias_temp_min = temp_function(df_drias_filtre)
    val_ref_drias = calcul_val_reference(df_drias_temp_min, indicateur)
    df_drias_temp_min = calcule_anomalie(df_drias_temp_min, indicateur, val_ref_drias)

    # Anomalie et rolling average sur DRIAS
    # Anomalie et rolling average sur DRIAS
    df_drias_temp_min["rolling_avg"] = (
        df_drias_temp_min[indicateur].rolling(window=30).mean() - val_ref_drias
    )
    df_drias_temp_min["rolling_std"] = (
        df_drias_temp_min[indicateur].rolling(window=30).std()
    )
    df_drias_temp_min["avg + std"] = (
        df_drias_temp_min["rolling_avg"] + df_drias_temp_min["rolling_std"]
    )
    df_drias_temp_min["avg - std"] = (
        df_drias_temp_min["rolling_avg"] - df_drias_temp_min["rolling_std"]
    )

    df_mf_temp_min = df_mf_temp_min[
        (df_mf_temp_min["Année"] != 2024) & (df_mf_temp_min["Année"] != 1958)
    ]
    # Trace
    fig = plot_climate_strip(
        df_mf_temp_min,
        df_drias_temp_min,
        indicateur,
        periode_start,
        periode_end,
        dict_indicateurs,
        val_ref,
        1951,
        1980,
    )

    return fig, df_drias_temp_min, df_mf_temp_min


def calcul_val_reference(df, indic):
    df_periode = df[(df["Année"] >= 1951) & (df["Année"] <= 1980)]

    moyenne = df_periode[indic].mean()

    return moyenne


def calcule_anomalie(df, indicateur, moyenne_ref):
    df["ANOM_" + indicateur] = df[indicateur] - moyenne_ref
    return df


def main_indic_nb_jour_consecutif(
    df_mf,
    df_drias,
    seuil,
    periode_start,
    periode_end,
    dict_indicateurs,
    signe,
):
    indicateur = "Nb_jours_max"
    # filtre temporel
    df_mf_filtre = filtre_temporel_periode(df_mf, periode_start, periode_end)
    df_drias_filtre = filtre_temporel_periode(df_drias, periode_start, periode_end)

    # filtre  et calcul nb jour sur MF
    df_mf_nb_jour = calc_nb_j(df_mf_filtre, seuil, signe)
    val_ref = calcul_val_reference(df_mf_nb_jour, indicateur)
    df_mf_nb_jour = calcule_anomalie(df_mf_nb_jour, indicateur, val_ref)

    # fitlre et calcul sur DRIAS
    df_drias_nb_jour = calc_nb_j(df_drias_filtre, seuil, signe)
    val_ref_drias = calcul_val_reference(df_drias_nb_jour, indicateur)
    df_drias_nb_jour = calcule_anomalie(df_drias_nb_jour, indicateur, val_ref_drias)

    # Annomalie et rolling average sur DRIAS
    df_drias_nb_jour["rolling_avg"] = (
        df_drias_nb_jour[indicateur].rolling(window=30).mean() - val_ref_drias
    )
    df_drias_nb_jour["rolling_std"] = (
        df_drias_nb_jour[indicateur].rolling(window=30).std()
    )
    df_drias_nb_jour["avg + std"] = (
        df_drias_nb_jour["rolling_avg"]
        + df_drias_nb_jour["rolling_std"]  # *(1+(df_drias_nb_jour["Année"]-2000)/50)
    )
    df_drias_nb_jour["avg - std"] = (
        df_drias_nb_jour["rolling_avg"] - df_drias_nb_jour["rolling_std"]
    )
    df_mf_nb_jour = df_mf_nb_jour[
        (df_mf_nb_jour["Année"] != 2024) & (df_mf_nb_jour["Année"] != 1958)
    ]

    # Trace
    fig = plot_climate_strip(
        df_mf_nb_jour,
        df_drias_nb_jour,
        indicateur,
        periode_start,
        periode_end,
        dict_indicateurs,
        val_ref,
        1951,
        1980,
    )

    return fig, df_drias_nb_jour, df_mf_nb_jour


def prepa_df_metrique(df, ref, indicateur, longueur_horizon=15):
    df_filtre_horizon = filter_horizon(
        df, reference=ref, longueur_horizon=longueur_horizon
    )
    return int(df_filtre_horizon[indicateur].mean())


def filter_horizon(df, reference, longueur_horizon=15):
    df_filtre = df[
        (df["Année"] >= reference - longueur_horizon)
        & (df["Année"] <= reference + longueur_horizon)
    ]
    # reference_date = pd.Timestamp(year=reference, month=1, day=1)
    # date_before = reference_date - pd.DateOffset(years=longueur_horizon)
    # date_after = reference_date + pd.DateOffset(years=longueur_horizon)
    # filtered_df = df[(df["DATE"] >= date_before) & (df["DATE"] <= date_after)]
    return df_filtre


# Partie Regression
def create_df_index_var_metier(df_m, df_var_metier):
    df_m.rename(columns={"Année": "DATE"}, inplace=True)
    df_var_metier.rename(
        columns={list(df_var_metier)[0]: 0, list(df_var_metier)[1]: 1}, inplace=True
    )
    df = df_m.merge(df_var_metier, left_on="DATE", right_on=1)
    return df


def corr_df(df):
    return df[["index", 0]].corr()  # [0]["index"]


def modele_baseline_train(df):
    X, Y, annee = df[["index"]], df[0], df["DATE"]

    regr = DecisionTreeClassifier()
    regr.fit(X, Y)

    return regr


def predict(df, model):

    df = df[df["Année"] > 2024]
    annee_drias = df["Année"]

    df.rename(columns={list(df)[1]: "index"}, inplace=True)

    y_pred = model.predict(df[["index"]])

    return y_pred, annee_drias


def create_df_pred(y_pred, annee):

    df_predictions = pd.DataFrame({0: y_pred, 1: annee})

    return df_predictions


def plot_reg(df, regr):
    y_pred = regr.predict(df[["index"]])
    fig = go.Figure()
    # Add traces
    X, _, _ = df[["index"]], df[0], df["DATE"]

    fig.add_trace(
        go.Scatter(x=df["index"], y=df[0], mode="markers", name="Observations")
    )
    fig.add_trace(
        go.Scatter(x=df["index"], y=y_pred, mode="lines+markers", name="Predictions")
    )

    fig.update_layout(
        title="Comparaison des Observations et des Prédictions",
        xaxis_title="Index Climatique",
        yaxis_title="Variable business",
    )
    return fig


def plot_reg_temporel(df, regr, df_drias):
    annee = df["DATE"]
    Y = df[0]
    y_pred = regr.predict(df[["index"]])

    df_drias = df_drias[df_drias["Année"] > 2024]
    annee_drias = df_drias["Année"]

    df_drias.rename(columns={list(df_drias)[1]: "index"}, inplace=True)
    y_pred_drias = regr.predict(df_drias[["index"]])

    fig = go.Figure()
    # Add traces
    fig.add_trace(go.Scatter(x=annee, y=Y, mode="markers", name="observations"))
    fig.add_trace(
        go.Scatter(
            x=annee_drias,
            y=y_pred_drias,
            mode="lines+markers",
            name="predictions DRIAS",
        )
    )
    fig.add_trace(
        go.Scatter(x=annee, y=y_pred, mode="lines+markers", name="predictions")
    )
    fig.update_layout(xaxis_title="Annee", yaxis_title="variable")
    return fig


# def main_inspect_csv(df_ind, df_mf, df_drias):
#    df = create_df_index_var_metier(df_mf, df_ind)
#    corr = corr_df(df)
#    # st.write(f"Correlation entre la variable et l'indicateur climatique : \n{}")
#
#    regr = modele_baseline_train(df)
#    fig1 = plot_reg(df, regr)
#    fig2 = plot_reg_temporel(df, regr, df_drias)
#    return corr, fig1, fig2


def main_inspect_csv(df_ind, df_mf, df_drias):
    df = create_df_index_var_metier(df_mf, df_ind)
    regr = modele_baseline_train(df)
    y_pred, annee_drias = predict(df_drias, regr)
    df_qualite_pred = create_df_pred(y_pred, annee_drias)
    df_concat = pd.concat([df_ind, df_qualite_pred], axis=0)
    df_concat = df_concat.rename(columns={0: "qualite", 1: "Année"})
    df_1995 = filter_horizon(df_concat, 1995, longueur_horizon=15)
    df_2030 = filter_horizon(df_concat, 2030, longueur_horizon=15)
    df_2050 = filter_horizon(df_concat, 2050, longueur_horizon=15)
    return df_1995, df_2030, df_2050


def show_serie_tempo(
    df_metier, df_mf, variable_metier, unite_mesure_mf, unite_mesure_bus, indicateur_mf
):
    df_mf = df_mf.merge(df_metier, on="Année")[df_mf.columns]
    fig = go.Figure()

    # Ajout de la courbe pour df_m
    fig.add_trace(
        go.Scatter(
            x=df_mf["Année"],
            y=df_mf["index"],
            mode="lines+markers",
            name=indicateur_mf,
            yaxis="y",
        )
    )

    # Ajout de la courbe pour df_metier
    fig.add_trace(
        go.Scatter(
            x=df_metier["Année"],
            y=df_metier["var_buis"],
            mode="lines",
            name=variable_metier,
            yaxis="y2",
        )
    )

    ## Personnalisation des légendes
    fig.update_layout(
        title={
            "text": f"Evolution de la {indicateur_mf.lower()} et de la {variable_metier.lower()} en fonction du temps."
        },
        legend=dict(
            title="Légende",
            # x=0.01, y=0.99,
            bgcolor="rgba(255, 255, 255, 0.5)",
            bordercolor="black",
            borderwidth=1,
        ),
        legend2=dict(
            title="Légende 2",
            # x=0.01, y=0.95,
            bgcolor="rgba(255, 255, 255, 0.5)",
            bordercolor="black",
            borderwidth=1,
        ),
    )

    # Ajout du double axe y
    fig.update_layout(
        yaxis2=dict(
            title=f"{variable_metier}" + unite_mesure_mf, overlaying="y", side="right"
        )
    )

    ## Ajout des labels pour les axes
    fig.update_layout(
        xaxis_title="Année",
        yaxis_title=f"{indicateur_mf}" + unite_mesure_mf,
        yaxis2_title=f"{variable_metier}" + "("+unite_mesure_bus+")",
    )

    return fig


def show_box_plot(df95, df30, df50, scenario, variable_metier, unite_mesure):

    fig = go.Figure()

    fig.add_trace(
        go.Box(
            y=df95["qualite"],
            name="Horizon 1995",
            marker=dict(color="blue"),
            boxmean=True,
            jitter=0.3,
            pointpos=-1.8,
        )
    )

    fig.add_trace(
        go.Box(
            y=df30["qualite"],
            name="Horizon 2030",
            marker=dict(color="red"),
            boxmean=True,
            jitter=0.3,
            pointpos=0,
        )
    )

    fig.add_trace(
        go.Box(
            y=df50["qualite"],
            name="Horizon 2050",
            marker=dict(color="green"),
            boxmean=True,
            jitter=0.3,
            pointpos=1.8,
        )
    )

    fig.update_layout(
        title=f"Box Plot de la {variable_metier} ({unite_mesure}) pour chaque horizon pour le scenario {scenario}",
        yaxis_title=f"{variable_metier} ({unite_mesure})",
        xaxis_title="Horizons",
    )

    return fig


def validate_date(date_text):
    try:
        # Check if the date is in the correct format
        datetime.strptime(date_text, "%m-%d")
        return True
    except ValueError:
        return False


text_explication_fin = """     
- **Données brutes collectées :**
    - Données quotidiennes du modèle de simulation des schémas de surface (Safran - Isba) (pour l’instant uniquement les températures, mais précipitations, humidité et vents envisagés)
    - Données DRIAS : Projections climatiques régionalisées réalisées dans les laboratoires français de modélisation du climat
    - Données externes importables via l’interface  

    
- **Les données sont préparées et traitées afin de permettre la production d’indicateurs personnalisés sur l’historique, selon les scénarios climatiques et sur une période temporelle personnalisée (été, hiver, mois de mars, ..) :**
    - Température maximal, minimum et moyenne
    - Nombre de jours dont la température moyenne dépasse un seuil à définir
    - Nombre de période de jours dont la température moyenne dépasse un seuil à définir
    - Comparaison et corrélation par rapport aux données externes importés

- **Via une interface web streamlit, il est possible de:**
    - Importer des données externes utiles pour le métier
    - Personnaliser les indicateurs (période temporelle, seuil, etc..)
    - Visualiser les indicateurs sous forme de graphique ou de KPI et de les exporter
              
- **Impact envisagé :** 
    - La solution permet de produire simplement des indicateurs personnalisés sur les données d’historiques météos, les projections climatiques et des données externes**
    """


def load_data():
    return pd.read_csv("data/qualite_vin.csv")


data = load_data()


def download_csv():
    csv = data.to_csv(index=False)
    return csv

def compute_correlation(df_indicateur, df_metier):
    df_merge = df_indicateur.merge(df_metier, on = "Année")
    res = df_merge.corr()
    correlation = res.loc["var_buis", "index"]
    return correlation