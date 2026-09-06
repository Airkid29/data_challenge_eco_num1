"""Point d'entrée Streamlit pour le déploiement Cloud de Togo Connect.

Ne pas sélectionner app.py dans Streamlit Cloud : ce fichier lance Flask.
"""
from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px

from app import COLORS, DATA, commune_metrics, fmap

st.set_page_config(page_title="Togo Connect | Atlas numérique", page_icon="◈", layout="wide")

st.markdown("""<style>
    .stApp { background:#0a1014; color:#eef5f3; }
    [data-testid="stSidebar"] { background:#0d1419; }
    [data-testid="stMetric"] { background:#10181e; border:1px solid #27353c; border-radius:8px; padding:15px; }
    h1,h2,h3 { color:#eef5f3; } .stCaption { color:#91a4a1; }
    div[data-baseweb="select"] > div { background:#10181e; }
</style>""", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def compute_metrics(region: str, service: str):
    data = DATA.copy()
    if region != "Toutes":
        data = data[data.region_nom_bdd.eq(region)]
    if service != "Tous":
        data = data[data.service.eq(service)]
    communes = commune_metrics(data)
    regional = communes.groupby("region_nom_bdd", as_index=False).agg(
        population=("pop", "sum"), points=("points", "sum"),
        mobile_money=("mm", "sum"), fixe=("fixed", "sum"), services=("services", "max"),
    )
    regional["points_10k"] = regional.points / regional.population * 10_000
    regional["mm_10k"] = regional.mobile_money / regional.population * 10_000
    regional["fixe_100k"] = regional.fixe / regional.population * 100_000
    regional = regional.sort_values("points_10k")

    # Le score de priorité utilise toujours toutes les couches : isoler Mobile Money
    # ou une agence dans le filtre ne doit pas modifier la stratégie nationale.
    complete = DATA if region == "Toutes" else DATA[DATA.region_nom_bdd.eq(region)]
    priorities = commune_metrics(complete)
    priorities["score"] = (
        (1 - priorities.mm_density.rank(pct=True)) * 50
        + priorities["pop"].rank(pct=True) * 25
        + priorities.fixed.eq(0).astype(int) * 25
    ).round().astype(int)
    return data, communes, regional, priorities


with st.sidebar:
    st.title("◈ Togo Connect")
    st.caption("ATLAS NUMÉRIQUE · DÉFI 2")
    page = st.radio("Navigation", ["Vue d'ensemble", "Accès & équité", "Cartographie", "Priorisation", "Données & méthode"])
    st.divider()
    regions = ["Toutes", *sorted(DATA.region_nom_bdd.dropna().unique())]
    services = ["Tous", *sorted(DATA.service.unique())]
    region = st.selectbox("Périmètre géographique", regions)
    service = st.selectbox("Service analysé", services)
    st.divider()
    st.caption("Sources : Géodata Togo · RGPH-5 2022")
    st.caption("19 971 points · 5 régions")

data, communes, regional, priorities = compute_metrics(region, service)
population = communes["pop"].sum()
density = data.shape[0] / population * 10_000 if population else 0

st.caption("DIAGNOSTIC TERRITORIAL · TOGO")
titles = {
    "Vue d'ensemble": ("Vue d'ensemble", "Le maillage des services numériques, sans confondre présence de points et couverture mobile."),
    "Accès & équité": ("Accès & équité territoriale", "Comparer les services recensés à la population RGPH-5 2022."),
    "Cartographie": ("Cartographie des infrastructures", "Explorer les agences, data centers et points de finance digitale."),
    "Priorisation": ("Communes à investiguer", "Un portefeuille transparent pour guider les analyses et déploiements suivants."),
    "Données & méthode": ("Données, méthode & limites", "Ce que les données permettent de conclure — et ce qu'elles ne permettent pas encore."),
}
st.title(titles[page][0])
st.write(titles[page][1])

if page in {"Vue d'ensemble", "Accès & équité"}:
    a, b, c, d = st.columns(4)
    a.metric("Points cartographiés", f"{len(data):,}".replace(",", " "), "Dans le filtre actif")
    b.metric("Communes dotées", f"{data.commune_nom_bdd.nunique()}", "Au moins un point recensé")
    c.metric("Population rapprochée", f"{int(population):,}".replace(",", " "), "Communes RGPH-5 appariées")
    d.metric("Densité du service", f"{density:.1f}", "Points / 10 000 habitants")

if page == "Vue d'ensemble":
    left, right = st.columns((1.6, 1))
    with left:
        fig = px.bar(regional, x="points_10k", y="region_nom_bdd", orientation="h", color="points_10k",
                     color_continuous_scale=["#1e5147", "#27d3ad"], labels={"region_nom_bdd":"", "points_10k":"Points / 10 000 habitants"})
        fig.update_layout(height=370, coloraxis_showscale=False, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.subheader("Lecture rigoureuse")
        if not regional.empty:
            low = regional.iloc[0]
            st.info(f"**{low.region_nom_bdd}** a le maillage enregistré le plus faible : **{low.points_10k:.1f} points / 10 000 habitants**.")
        st.caption("C'est un déficit relatif de points recensés, pas une preuve de mauvaise couverture réseau.")
        st.markdown("**Conclusion défendable**\n\n- Les agents Mobile Money dominent le maillage observé.\n- Les infrastructures fixes sont plus rares et doivent être analysées séparément.\n- L'ajout de la couverture 2G/3G/4G est nécessaire avant de parler de zones blanches.")
    x, y = st.columns(2)
    with x:
        mix = data.groupby(["region_nom_bdd", "service"]).size().reset_index(name="points")
        fig = px.bar(mix, x="region_nom_bdd", y="points", color="service", barmode="stack", color_discrete_map=COLORS)
        fig.update_layout(height=350, template="plotly_dark", legend=dict(orientation="h", y=1.12))
        st.plotly_chart(fig, use_container_width=True)
    with y:
        fig = px.scatter(regional, x="population", y="points_10k", size="points", color="region_nom_bdd", text="region_nom_bdd",
                         labels={"population":"Population RGPH-5", "points_10k":"Points / 10 000 hab."})
        fig.update_layout(height=350, template="plotly_dark", showlegend=False)
        fig.update_traces(textposition="top center")
        st.plotly_chart(fig, use_container_width=True)

elif page == "Accès & équité":
    st.subheader("Trois lectures complémentaires — ne pas les additionner")
    st.dataframe(regional[["region_nom_bdd", "population", "mm_10k", "fixe_100k", "services"]].rename(columns={
        "region_nom_bdd":"Région", "population":"Population", "mm_10k":"Mobile Money /10k", "fixe_100k":"Fixe /100k", "services":"Services distincts"}),
        use_container_width=True, hide_index=True, column_config={"Population": st.column_config.NumberColumn(format="%d"), "Mobile Money /10k": st.column_config.NumberColumn(format="%.1f"), "Fixe /100k": st.column_config.NumberColumn(format="%.2f")})
    fig = px.scatter(regional, x="population", y="mm_10k", size="mobile_money", color="fixe_100k", hover_name="region_nom_bdd",
                     color_continuous_scale="Teal", labels={"population":"Population", "mm_10k":"Mobile Money /10k", "fixe_100k":"Fixe /100k"})
    fig.update_layout(height=440, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Mobile Money mesure une proximité de service financier ; l'infrastructure fixe décrit un autre type de présence. Aucun des deux indicateurs ne mesure la qualité ou la couverture mobile.")

elif page == "Cartographie":
    st.caption("Utilise le contrôle en haut à droite de la carte pour activer ou masquer les couches.")
    components.html(fmap(data), height=700, scrolling=False)

elif page == "Priorisation":
    st.info("Score d'investigation : 50 % faible densité Mobile Money + 25 % population à servir + 25 % absence d'infrastructure fixe. Il ne désigne pas une zone blanche.")
    table = priorities.sort_values(["score", "pop"], ascending=False).head(20)
    st.dataframe(table[["commune_nom_bdd", "region_nom_bdd", "pop", "mm_density", "fixed", "score"]].rename(columns={
        "commune_nom_bdd":"Commune", "region_nom_bdd":"Région", "pop":"Population", "mm_density":"Mobile Money /10k", "fixed":"Infrastructure fixe", "score":"Score /100"}),
        use_container_width=True, hide_index=True)
    fig = px.scatter(priorities, x="pop", y="mm_density", size="points", color="score", hover_name="commune_nom_bdd",
                     color_continuous_scale=["#27d3ad", "#f8b84e", "#ee736a"], labels={"pop":"Population", "mm_density":"Mobile Money /10k", "score":"Score"})
    fig.update_layout(height=440, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

else:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Données utilisées")
        st.markdown("- 19 788 points Mobile Money\n- 180 agences fixes et 3 data centers\n- Population résidente RGPH-5 2022\n- Limites administratives")
        st.subheader("Raccordement")
        st.write(f"{len(communes)} communes raccordées automatiquement sur {data.commune_nom_bdd.nunique()} communes observées dans le périmètre.")
    with col2:
        st.subheader("Limites à assumer")
        st.warning("Les données de couverture 2G/3G/4G/5G et de qualité de signal ne sont pas présentes. Le tableau de bord ne calcule donc pas de zones blanches.")
        st.subheader("Étape suivante")
        st.write("Ajouter les couches de couverture par technologie et opérateur, puis croiser avec la population pour estimer la population réellement non desservie.")
