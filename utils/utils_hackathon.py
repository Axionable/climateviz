import plotly.express as px
import pandas as pd
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go


def hello():
    return "Hello"


# Luigia
def plot_climate_strips(df, indicateur, periode_start, periode_end, dict_indicateurs):
    fig = px.line(
        df,
        x="ANNEE",
        y="rolling_avg",
        labels={"rolling_avg": "Écart à la moyenne (°C)", "ANNEE": "Année"},
        color_discrete_sequence=["green"],
        title=f"{dict_indicateurs[indicateur]} entre le {periode_start} et le {periode_end}.<br>Écart à la moyenne de référence 1951 à 1980",
    )
    # changer unité de la valeur

    fig.add_bar(
        x=df["ANNEE"],
        y=df["ANOM_" + indicateur],
        name=f"{indicateur} (°C)",
        marker=dict(color=df[indicateur], coloraxis="coloraxis"),
    )
    fig.update_layout(coloraxis=dict(colorscale="RdYlBu_r"), width=1000)
    fig.update_traces(hovertemplate="Année: %{x}<br>Anomalie: %{y:.1f}°")

    return fig


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


# tania
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


def apply_fct(df, func):
    return df.apply(func)


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
    result = df.groupby(["Année"])["T_Q"].min().reset_index()
    result.rename(columns={"T_Q": "T_MOYENNE"}, inplace=True)
    return result


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


def plot_climate_strips_tania(
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
    # a modifier les données en DUR @lucas
    fig = go.Figure()

    fig.add_bar(
        x=df["Année"],
        y=df["ANOM_" + indicateur],
        name=f"{indicateur}",
        marker=dict(color=df[indicateur], coloraxis="coloraxis"),
    )
    fig.update_layout(coloraxis=dict(colorscale="RdYlBu_r"), width=1000)
    fig.update_traces(hovertemplate="Année: %{x}<br>Anomalie: %{y:.1f}°")

    fig.update_layout(
        title=f"{dict_indicateurs[indicateur]} entre le {periode_start} et le {periode_end}.<br>Écart à la moyenne de référence {start_year_ref} à {end_year_ref}",
        xaxis_title="Année",
        yaxis_title="Anomalie (Nombre de jours)",
        width=1000,
    )

    fig.update_yaxes(
        title_text="Anomalie (°C)", tickvals=[0], ticktext=[f"Moyenne: {moy_ref:.2f} "]
    )

    fig.update_traces(hovertemplate="Année: %{x}<br>Anomalie: %{y:.1f}°")

    # Ajout de la deuxième partie du graphique
    fig2 = px.line(
        df_drias,
        x="Année",
        y="rolling_avg",
        labels={"rolling_avg": "Écart à la moyenne (°C)", "Année": "Année"},
        color_discrete_sequence=["green"],
        title=f"{dict_indicateurs[indicateur]} entre le {periode_start} et le {periode_end}.<br>Écart à la moyenne de référence {start_year_ref}-{end_year_ref+30}",
    )
    fig2.add_scatter(
        x=df_drias["Année"],
        y=df_drias["avg + std"],
        mode="lines",
        line=dict(width=0),
        fill="tonexty",
        fillcolor='rgba(204, 204, 204, 0.2)'
    )
    fig2.add_scatter(
        x=df_drias["Année"],
        y=df_drias["avg - std"],
        mode="lines",
        line=dict(width=0),
        fill="tonexty",
        fillcolor='rgba(204, 204, 204, 0.2)'
    )
    fig2.update_layout(coloraxis=dict(colorscale="RdYlBu_r"))
    fig2.update_traces(hovertemplate="Année: %{x}<br>Anomalie: %{y:.1f}°")

    for data in fig2.data:
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
    result = df.groupby(["Année"])["T_Q"].min().reset_index()
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
    elif indicateur =="T_MIN":
        temp_function = temp_min
    elif indicateur =="T_MOYENNE":
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

    # Annomalie et rolling average sur DRIAS
    df_drias_temp_min["rolling_avg"] = (
        df_drias_temp_min[indicateur].rolling(window=30).mean() - 15
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
    print(df_mf_temp_min.head(5))
    # Trace
    fig = plot_climate_strips_tania(
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

    return fig

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
    indicateur,
    seuil,
    periode_start,
    periode_end,
    dict_indicateurs,
    signe,
):
    # df = filtre_temporel_periode(df, periode_start, periode_end)
    # df_2 = calc_nb_j(df, seuil, signe)
    # moy_ref = moyenne_T_Q(df_2, indicateur)
    # df_2 = calcule_anomalie(df_2, indicateur, moy_ref)
    # fig = plot_climate_strips(df_2, indicateur, periode_start, periode_end, dict_indicateurs, moy_ref)

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
        df_drias_nb_jour[indicateur].rolling(window=30).mean() - 15
    )
    df_drias_nb_jour["rolling_std"] = (
        df_drias_nb_jour[indicateur].rolling(window=30).std()
    )
    df_drias_nb_jour["avg + std"] = (
        df_drias_nb_jour["rolling_avg"] + df_drias_nb_jour["rolling_std"]
    )
    df_drias_nb_jour["avg - std"] = (
        df_drias_nb_jour["rolling_avg"] - df_drias_nb_jour["rolling_std"]
    )
    # Trace
    fig = plot_climate_strips_tania(
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

    return fig


# paul-etienne
def create_df_index_var_metier(df_index, df_var_metier):
    df_var_metier.rename(columns={list(df_var_metier)[0]: 0}, inplace=True)
    df_var_metier.rename(columns={list(df_var_metier)[1]: 1}, inplace=True)
    df_index.rename(columns={list(df_index)[0]: "DATE"}, inplace=True)
    df_index.rename(columns={list(df_index)[1]: "index"}, inplace=True)

    df = df_index.merge(df_var_metier, left_on="DATE", right_on=1)

    return df


def load_csv(df_index):
    uploaded_file = st.file_uploader(
        "Charger un fichier csv (col1 : variable, col2 : année)"
    )
    if uploaded_file is not None:
        df_var_metier = pd.read_csv(uploaded_file)
        print("Chargé")
        # st.write(df_var_metier)

    return create_df_index_var_metier(df_index, df_var_metier)


def corr_df(df):
    return df[["index", 0]].corr()  # [0]["index"]


def modele_baseline_train(df):
    X, Y, annee = df[["index"]], df[0], df["DATE"]

    regr = LinearRegression()
    regr.fit(X, Y)

    return regr


def plot_reg(df, regr):
    y_pred = regr.predict(df[["index"]])
    fig = go.Figure()
    # Add traces
    X, _, _ = df[["index"]], df[0], df["DATE"]

    fig.add_trace(
        go.Scatter(x=df["index"], y=df[0], mode="markers", name="observations")
    )
    fig.add_trace(
        go.Scatter(x=df["index"], y=y_pred, mode="lines+markers", name="predictions")
    )

    fig.update_layout(xaxis_title="index climatique", yaxis_title="variable")
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


def main_inspect_csv(df_ind, df_mf, df_drias):
    # df = load_csv (df_index)
    df = create_df_index_var_metier(df_mf, df_ind)
    corr = corr_df(df)
    # st.write(f"Correlation entre la variable et l'indicateur climatique : \n{}")

    regr = modele_baseline_train(df)
    fig1 = plot_reg(df, regr)
    fig2 = plot_reg_temporel(df, regr, df_drias)
    return corr, fig1, fig2