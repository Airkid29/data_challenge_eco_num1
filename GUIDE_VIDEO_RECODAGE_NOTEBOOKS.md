# Guide complet pour la video YouTube

## Refaire une analyse de l'inclusion numerique au Togo, de A a Z

Ce document est un support de tournage et de recodage. Il est destine a quelqu'un qui debute en Python, en analyse de donnees et en cartographie.

L'objectif de la video est de construire progressivement une analyse repondant a trois questions :

1. Ou sont situes les points de services numeriques au Togo ?
2. Les points sont-ils repartis de la meme facon entre les regions et les communes ?
3. Quelles communes devraient etre examinees en priorite ?

Le projet utilise des donnees d'agences Moov, Togocom, Telecom, CANAL+, de data centers et d'agents Mobile Money, ainsi que des donnees de population et des limites administratives.

---

## 1. Ce que tu vas construire

A la fin de la video, tu auras une chaine en quatre etapes :

```text
01 exploration       -> comprendre les fichiers
02 nettoyage         -> harmoniser et sauvegarder les donnees
03 analyse spatiale  -> placer les points sur la carte du Togo
04 indicateurs       -> calculer les densites et priorites
```

Les notebooks correspondants sont :

- [01_exploration.ipynb](notebooks/01_exploration.ipynb)
- [02_nettoyage.ipynb](notebooks/02_nettoyage.ipynb)
- [03_analyse_spatiale.ipynb](notebooks/03_analyse_spatiale.ipynb)
- [04_indicateurs.ipynb](notebooks/04_indicateurs.ipynb)

Ne commence pas par le dashboard. Le dashboard consomme deja les memes donnees et les memes indicateurs. Pour la video, pars des donnees brutes et construis le raisonnement.

---

## 2. Vocabulaire essentiel

### DataFrame

Un DataFrame est un tableau de donnees manipule par pandas. Une ligne represente souvent un point de service et une colonne represente une information : region, commune, nom, coordonnees, etc.

### GeoDataFrame

Un GeoDataFrame est un DataFrame auquel on ajoute une geometrie. Ici, chaque ligne peut contenir un point geographique.

### CSV

Un fichier CSV est un tableau texte. Les fichiers `moov.csv`, `Togocom.csv` et `mobile money.csv` sont des exemples de CSV.

### GeoJSON

Un fichier GeoJSON contient des geometries geographiques. Les fichiers de regions, communes, cantons et prefectures sont des limites administratives.

### WKT et POINT

Les CSV stockent les coordonnees dans une colonne `geometry`, par exemple :

```text
POINT (1.1388047548912492 8.989586208250028)
```

Le premier nombre est la longitude et le second est la latitude.

### CRS / EPSG:4326

Le CRS indique comment interpreter les coordonnees. `EPSG:4326` correspond aux coordonnees longitude/latitude habituelles du GPS.

### Jointure spatiale

Une jointure spatiale repond a une question comme : « dans quelle commune se trouve ce point ? ». Elle compare la position du point avec le polygone de la commune.

### Densite

Une densite compare le nombre de points a la population. Elle est plus informative qu'un simple total, car une grande region aura naturellement plus de points.

```text
points pour 10 000 habitants = nombre de points / population * 10 000
```

### Limite importante

Un point recense ne signifie pas necessairement qu'il est ouvert, performant ou accessible a tous. Ces notebooks mesurent une presence dans les donnees, pas la qualite de la couverture reseau.

---

## 3. Preparation de l'environnement

### 3.1 Ouvrir le bon dossier

Dans VS Code, ouvre le dossier racine :

```text
Togo_Digital_Challenge
```

Le terminal doit etre positionne dans ce dossier. Verifie-le avec :

```powershell
Get-Location
```

Tu dois voir un chemin qui finit par `Togo_Digital_Challenge`.

### 3.2 Installer les dependances

Le projet utilise Python. Dans un terminal PowerShell, execute :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r dashboard\requirements.txt
python -m pip install jupyter ipykernel geopandas matplotlib seaborn openpyxl
```

Si PowerShell bloque l'activation, utilise directement l'interpreteur de l'environnement :

```powershell
.\.venv\Scripts\python.exe -m pip install -r dashboard\requirements.txt
.\.venv\Scripts\python.exe -m pip install jupyter ipykernel geopandas matplotlib seaborn openpyxl
```

Dans VS Code, ouvre un notebook puis selectionne le kernel Python de `.venv`.

### 3.3 Regle de tournage

Pour chaque notebook :

1. explique l'objectif avant d'ecrire le code ;
2. retape une petite portion ;
3. execute la cellule ;
4. lis le resultat a l'ecran ;
5. explique ce que le resultat signifie ;
6. seulement ensuite continue.

Ne colle pas tout le code d'un coup dans la video. Le spectateur doit voir le raisonnement se construire.

---

## 4. Structure des dossiers

Avant de commencer, montre cette structure :

```text
Togo_Digital_Challenge/
|-- data/
|   |-- raw/              donnees originales
|   |-- processed/        sorties du nettoyage
|-- notebooks/
|   |-- 01_exploration.ipynb
|   |-- 02_nettoyage.ipynb
|   |-- 03_analyse_spatiale.ipynb
|   |-- 04_indicateurs.ipynb
|-- outputs/
|   |-- figures/
|   |-- maps/
|   |-- tables/
|-- dashboard/
```

La regle a retenir est simple :

- `data/raw` ne doit pas etre modifie ;
- `data/processed` contient les donnees nettoyees ;
- `outputs` contient les resultats visibles ;
- `notebooks` contient le raisonnement et le code.

---

# Notebook 1 - Exploration

## Objectif a annoncer

> « Je ne nettoie encore rien. Je veux d'abord savoir quels fichiers existent, combien de lignes ils contiennent et quelles colonnes ils proposent. »

Ouvre [01_exploration.ipynb](notebooks/01_exploration.ipynb).

## Etape 1 : importer les bibliotheques

Explique :

- `Path` gere les chemins de fichiers ;
- `pandas` lit les tableaux ;
- `geopandas` lit les fichiers geographiques.

Code a retaper :

```python
from pathlib import Path
import pandas as pd
import geopandas as gpd
```

## Etape 2 : definir les chemins

```python
PROJECT_DIR = Path.cwd()
if PROJECT_DIR.name == "notebooks":
    PROJECT_DIR = PROJECT_DIR.parent
RAW_DIR = PROJECT_DIR / "data" / "raw"
```

Explique que `Path.cwd()` renvoie le dossier courant. Le test sur `notebooks` permet au code de fonctionner si le notebook est lance depuis le dossier racine ou depuis le dossier `notebooks`.

## Etape 3 : decrire les sources

```python
SOURCE_PATTERNS = {
    "Moov": "moov.csv",
    "Togocom": "Togocom.csv",
    "Telecom": "file-Agences*.csv",
    "CANAL+": "canalplus.csv",
    "Data center": "datacenter.csv",
    "Mobile Money": "mobile money.csv",
}
```

Le motif `file-Agences*.csv` est volontaire : le nom complet contient une date et des caracteres accentues. Le caractere `*` evite de rendre le code dependant du nom exact.

## Etape 4 : trouver et lire un fichier

```python
def find_source(pattern):
    matches = list(RAW_DIR.glob(pattern))
    return matches[0] if matches else None


def read_csv_safe(path):
    for encoding in ("utf-8-sig", "latin1"):
        try:
            return pd.read_csv(path, encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Encodage impossible : {path.name}")
```

A expliquer : certains fichiers utilisent UTF-8, d'autres un encodage ancien. On essaie donc deux encodages au lieu de supposer que tous les fichiers sont identiques.

## Etape 5 : produire un catalogue

```python
dfs = {}
source_summary = []

for service, pattern in SOURCE_PATTERNS.items():
    path = find_source(pattern)
    if path is None:
        print(f"Fichier absent : {pattern}")
        continue
    frame = read_csv_safe(path)
    dfs[service] = frame
    source_summary.append({
        "service": service,
        "fichier": path.name,
        "lignes": len(frame),
        "colonnes": len(frame.columns),
    })

catalogue = pd.DataFrame(source_summary)
display(catalogue)
```

Resultat attendu : six sources CSV, dont environ 19 788 lignes pour Mobile Money et quelques dizaines de lignes pour les operateurs et les data centers.

## Etape 6 : regarder les colonnes

```python
for service, frame in dfs.items():
    print(service, frame.columns.tolist())
    display(frame.head(3))
```

Observe notamment :

- `region_nom_bdd` ;
- `commune_nom_bdd` ;
- `etab_nom` ;
- `geometry`.

## Etape 7 : charger les limites administratives

```python
GEOJSON_PATTERNS = {
    "Régions": "Limites administratives - Régions.json",
    "Préfectures": "Limites administratives - Préféctures.json",
    "Communes": "Limites administratives - Communes.json",
    "Cantons": "Limites administratives - Cantons.json",
}

gdfs = {}
for level, filename in GEOJSON_PATTERNS.items():
    path = RAW_DIR / filename
    if path.exists():
        gdfs[level] = gpd.read_file(path)
        print(level, len(gdfs[level]), gdfs[level].crs)
```

Resultat attendu : 5 regions, 39 prefectures, 117 communes et 396 cantons.

## Conclusion a dire

> « J'ai maintenant le catalogue des donnees. Les fichiers ne sont pas encore prets pour l'analyse : ils n'ont pas tous le meme format, les coordonnees sont du texte et la population est dans un fichier Excel separe. Je vais donc nettoyer et harmoniser ces sources. »

---

# Notebook 2 - Nettoyage

## Objectif a annoncer

> « Je transforme plusieurs sources heterogenes en deux tables de reference : les points de services et la population par commune. »

Ouvre [02_nettoyage.ipynb](notebooks/02_nettoyage.ipynb).

## Etape 1 : imports et dossiers de sortie

```python
from pathlib import Path
import re
import unicodedata
import zipfile
import xml.etree.ElementTree as ET
import pandas as pd
import geopandas as gpd

PROJECT_DIR = Path.cwd()
if PROJECT_DIR.name == "notebooks":
    PROJECT_DIR = PROJECT_DIR.parent
RAW_DIR = PROJECT_DIR / "data" / "raw"
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
```

Explique que `mkdir` cree le dossier de sortie s'il n'existe pas.

## Etape 2 : nettoyer les textes

```python
def clean_text(value):
    if not isinstance(value, str):
        return value
    try:
        return value.encode("latin1").decode("utf-8") if "Ã" in value else value
    except UnicodeError:
        return value
```

Cette fonction corrige certains textes mal decodes comme `RÃ©gion` qui devrait etre `Région`.

La cle de jointure ignore les accents, espaces et caracteres speciaux :

```python
def normalize_key(value):
    value = clean_text(str(value)).upper()
    return re.sub(
        r"[^A-Z0-9]",
        "",
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode(),
    )
```

Ainsi `Kéran 2`, `KERAN-2` et `keran 2` peuvent etre compares plus facilement.

## Etape 3 : fusionner les CSV

Pour chaque source, ajoute :

- `service` : origine fonctionnelle du point ;
- `source_file` : fichier d'origine.

```python
frames = []
for service, pattern in SOURCE_PATTERNS.items():
    path = find_source(pattern)
    frame = read_csv_safe(path)
    frame.columns = [str(column).strip() for column in frame.columns]
    for column in frame.select_dtypes(include="object"):
        frame[column] = frame[column].map(clean_text)
    frame["service"] = service
    frame["source_file"] = path.name
    frames.append(frame)

raw_data = pd.concat(frames, ignore_index=True, sort=False)
```

Point pedagogique : `concat` empile les lignes. Les colonnes absentes d'un fichier sont completees par des valeurs manquantes.

## Etape 4 : transformer les geometries

```python
geometry = gpd.GeoSeries.from_wkt(raw_data["geometry"], on_invalid="ignore")
raw_data["lon"] = geometry.x
raw_data["lat"] = geometry.y

data_points = gpd.GeoDataFrame(
    raw_data,
    geometry=geometry,
    crs="EPSG:4326",
).dropna(subset=["lat", "lon"]).copy()
```

A expliquer : on transforme le texte WKT en vrais objets geographiques, puis on elimine uniquement les lignes sans coordonnees utilisables.

Ajoute les cles :

```python
data_points["region_key"] = data_points["region_nom_bdd"].map(normalize_key)
data_points["commune_key"] = data_points["commune_nom_bdd"].map(normalize_key)
data_points["nom"] = data_points.get("etab_nom", data_points["service"]).fillna(data_points["service"])
```

## Etape 5 : lire le fichier RGPH

Le fichier Excel fourni contient une feuille de styles invalide pour `openpyxl`. C'est pour cela que le notebook lit directement la feuille XML interne :

```python
population_file = RAW_DIR / "Population_residente_par_dcoupage_administratif_et_par_sexe.xlsx"
with zipfile.ZipFile(population_file) as archive:
    worksheet = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))

namespace = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
rows = [
    ["".join(cell.itertext()).strip() for cell in row][:4]
    for row in worksheet.findall(".//x:sheetData/x:row", namespace)
]
population_raw = pd.DataFrame(rows[1:], columns=["name", "sex", "unit", "pop"])
population_raw["pop"] = pd.to_numeric(population_raw["pop"], errors="coerce")
population = population_raw[
    population_raw["sex"].astype(str).str.casefold().eq("total")
].copy()
population["commune_key"] = population["name"].map(normalize_key)
population = population.groupby("commune_key", as_index=False)["pop"].max()
```

A dire simplement : le fichier est un classeur ZIP contenant du XML. On lit seulement la feuille utile et on ignore la feuille de styles defectueuse.

## Etape 6 : exporter les donnees communes

```python
data_points.drop(columns="geometry").to_csv(
    PROCESSED_DIR / "data_points.csv", index=False, encoding="utf-8"
)
data_points.to_file(
    PROCESSED_DIR / "data_points.geojson", driver="GeoJSON"
)
population.to_csv(
    PROCESSED_DIR / "population.csv", index=False, encoding="utf-8"
)
```

Puis verifie :

```python
print(len(data_points))
print(population["commune_key"].nunique())
print(data_points["service"].value_counts())
```

Resultat verifie dans ce projet :

- 19 971 points nettoyes ;
- 745 communes avec population ;
- 19 788 points Mobile Money ;
- 90 Telecom ;
- 62 Togocom ;
- 28 Moov ;
- 3 data centers.

## Conclusion a dire

> « Toutes les sources ont maintenant un format commun. Les deux sorties principales sont `data_points.geojson` pour la carte et `population.csv` pour les calculs de densite. »

---

# Notebook 3 - Analyse spatiale

## Objectif a annoncer

> « Je vais verifier que les points sont bien au Togo et comprendre comment ils se repartissent entre les communes et les services. »

Ouvre [03_analyse_spatiale.ipynb](notebooks/03_analyse_spatiale.ipynb).

## Etape 1 : charger les sorties du nettoyage

```python
from pathlib import Path
import geopandas as gpd
import matplotlib.pyplot as plt
import folium

PROJECT_DIR = Path.cwd()
if PROJECT_DIR.name == "notebooks":
    PROJECT_DIR = PROJECT_DIR.parent
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"
RAW_DIR = PROJECT_DIR / "data" / "raw"
OUTPUT_DIR = PROJECT_DIR / "outputs" / "maps"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

data_points = gpd.read_file(PROCESSED_DIR / "data_points.geojson")
communes = gpd.read_file(RAW_DIR / "Limites administratives - Communes.json")
```

## Etape 2 : verifier le CRS

```python
if data_points.crs != communes.crs:
    communes = communes.to_crs(data_points.crs)
```

Les deux couches doivent utiliser le meme CRS avant une comparaison geographique.

## Etape 3 : joindre les points aux communes

```python
points_hors_limites = gpd.sjoin(
    data_points,
    communes[["geometry"]],
    how="left",
    predicate="within",
)
data_points["dans_commune"] = points_hors_limites["index_right"].notna().to_numpy()
print(data_points["dans_commune"].mean() * 100)
```

Resultat verifie : environ 99,8 % des points se trouvent dans une commune. Les quelques points restants ne doivent pas etre supprimes sans analyse : ils peuvent venir d'une limite, d'une coordonnee ou d'un decalage geographique.

## Etape 4 : compter les points par region et service

```python
region_summary = (
    data_points.groupby(["region_nom_bdd", "service"], dropna=False)
    .size()
    .reset_index(name="points")
)
display(region_summary.sort_values("points", ascending=False).head(20))
```

Cette table permet de repondre a une premiere question : quelle region concentre les points recenses pour chaque service ?

## Etape 5 : produire une carte statique

```python
fig, ax = plt.subplots(figsize=(10, 8))
communes.boundary.plot(ax=ax, linewidth=0.35, color="#71817c")
data_points.plot(
    ax=ax,
    column="service",
    categorical=True,
    legend=True,
    markersize=8,
    alpha=0.75,
)
ax.set_title("Points de services numériques et limites communales")
ax.set_axis_off()
plt.tight_layout()
plt.show()
```

Explique que les limites donnent le contexte territorial et que les points montrent l'offre recensee.

## Etape 6 : produire une carte interactive

```python
map_togo = folium.Map(
    location=[8.7, 0.9],
    zoom_start=7,
    tiles="OpenStreetMap",
    control_scale=True,
)

for service, group in data_points.groupby("service"):
    layer = folium.FeatureGroup(name=service, show=True)
    for _, point in group.iterrows():
        folium.CircleMarker(
            location=[point.geometry.y, point.geometry.x],
            radius=4,
            fill=True,
            fill_opacity=0.8,
            tooltip=f"{service} - {point.get('nom', service)}",
            popup=f"{point.get('region_nom_bdd', '')}<br>{point.get('commune_nom_bdd', '')}",
        ).add_to(layer)
    layer.add_to(map_togo)

folium.LayerControl(collapsed=False).add_to(map_togo)
display(map_togo)
map_togo.save(OUTPUT_DIR / "services_numeriques.html")
```

Resultat : `outputs/maps/services_numeriques.html`.

## Conclusion a dire

> « La carte montre la localisation, mais elle ne suffit pas a comparer les territoires. Une region peut avoir beaucoup de points simplement parce qu'elle est plus peuplee. Je dois donc rapporter les points a la population. »

---

# Notebook 4 - Indicateurs

## Objectif a annoncer

> « Je transforme les points et la population en indicateurs comparables, puis je construis une liste de communes a investiguer. »

Ouvre [04_indicateurs.ipynb](notebooks/04_indicateurs.ipynb).

## Etape 1 : charger les sorties

```python
from pathlib import Path
import re
import unicodedata
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

PROJECT_DIR = Path.cwd()
if PROJECT_DIR.name == "notebooks":
    PROJECT_DIR = PROJECT_DIR.parent
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"
OUTPUT_DIR = PROJECT_DIR / "outputs" / "tables"
FIGURE_DIR = PROJECT_DIR / "outputs" / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FIGURE_DIR.mkdir(parents=True, exist_ok=True)
```

Recharge `data_points.csv` et `population.csv`. Reutilise la meme fonction `normalize_key` que dans le notebook 02.

## Etape 2 : construire les indicateurs par commune

Pour chaque commune, on calcule :

- `points` : tous les points recenses ;
- `mobile_money` : nombre d'agents Mobile Money ;
- `infrastructures` : points qui ne sont pas Mobile Money ;
- `services` : nombre de services distincts.

```python
commune_metrics = (
    data_points.groupby(["region_nom_bdd", "commune_nom_bdd"], dropna=False)
    .agg(
        points=("service", "size"),
        mobile_money=("service", lambda values: int((values == "Mobile Money").sum())),
        infrastructures=("service", lambda values: int((values != "Mobile Money").sum())),
        services=("service", "nunique"),
    )
    .reset_index()
)
```

Ensuite, on joint la population :

```python
commune_metrics["commune_key"] = commune_metrics["commune_nom_bdd"].fillna("").map(normalize_key)
commune_metrics = commune_metrics.merge(population, on="commune_key", how="left")
commune_metrics["pop"] = commune_metrics["pop"].fillna(0)
commune_metrics = commune_metrics[commune_metrics["pop"] > 0].copy()
```

Les communes sans population sont exclues des ratios, car une division par une population inconnue n'aurait pas de sens.

## Etape 3 : calculer les densites

```python
commune_metrics["points_per_10k"] = commune_metrics["points"] / commune_metrics["pop"] * 10000
commune_metrics["mobile_money_per_10k"] = commune_metrics["mobile_money"] / commune_metrics["pop"] * 10000
commune_metrics["infrastructures_per_100k"] = commune_metrics["infrastructures"] / commune_metrics["pop"] * 100000
```

Ne confonds pas les trois indicateurs :

- points / 10 000 habitants : maillage global ;
- Mobile Money / 10 000 habitants : proximite des services financiers ;
- infrastructures / 100 000 habitants : presence physique hors Mobile Money.

## Etape 4 : agregation regionale

```python
region_metrics = commune_metrics.groupby("region_nom_bdd", as_index=False).agg(
    population=("pop", "sum"),
    points=("points", "sum"),
    mobile_money=("mobile_money", "sum"),
    infrastructures=("infrastructures", "sum"),
)
region_metrics["points_per_10k"] = (
    region_metrics["points"] / region_metrics["population"] * 10000
)
region_metrics["mobile_money_per_10k"] = (
    region_metrics["mobile_money"] / region_metrics["population"] * 10000
)
```

Sauvegarde :

```python
region_metrics.to_csv(OUTPUT_DIR / "indicateurs_regions.csv", index=False)
commune_metrics.to_csv(OUTPUT_DIR / "indicateurs_communes.csv", index=False)
```

## Etape 5 : lire le graphique regional

Le graphique en barres compare les densites. Le nuage de points compare la population et l'intensite de desserte.

Resultat verifie sur les donnees actuelles :

- Kara : environ 30,1 points / 10 000 habitants ;
- Centrale : environ 26,6 ;
- Maritime : environ 25,7 ;
- Savanes : environ 23,5 ;
- Plateaux : environ 18,5.

Attention : cela ne signifie pas automatiquement que Kara est « mieux connectee ». Cela signifie seulement que les fichiers recensent davantage de points par habitant.

## Etape 6 : score de priorisation

Le score est une aide au ciblage, pas une verite absolue :

```text
50 % : faible densite Mobile Money
25 % : population importante
25 % : absence d'infrastructure fixe
```

Code :

```python
commune_metrics["priorite"] = (
    (1 - commune_metrics["mobile_money_per_10k"].rank(pct=True)) * 50
    + commune_metrics["pop"].rank(pct=True) * 25
    + commune_metrics["infrastructures"].eq(0).astype(int) * 25
).round().astype(int)

priorites = commune_metrics.sort_values(
    ["priorite", "pop"], ascending=False
).head(20)
priorites.to_csv(OUTPUT_DIR / "communes_prioritaires.csv", index=False)
```

Interprete le score ainsi : une commune avec un score eleve merite une investigation complementaire. Cela ne prouve pas qu'elle est une zone blanche.

## Conclusion a dire

> « J'ai maintenant des indicateurs comparables et une liste de communes a etudier. La prochaine etape serait de croiser ces resultats avec la couverture 2G, 3G et 4G, la qualite du signal, les routes, l'electricite et la frequentation des services. »

---

## 5. Ordre exact d'execution

Respecte cet ordre :

```text
1. 01_exploration.ipynb
2. 02_nettoyage.ipynb
3. 03_analyse_spatiale.ipynb
4. 04_indicateurs.ipynb
```

Entre chaque notebook, verifie que les sorties existent :

```text
apres 02 : data/processed/data_points.csv
apres 02 : data/processed/data_points.geojson
apres 02 : data/processed/population.csv
apres 03 : outputs/maps/services_numeriques.html
apres 04 : outputs/tables/indicateurs_regions.csv
apres 04 : outputs/tables/indicateurs_communes.csv
apres 04 : outputs/tables/communes_prioritaires.csv
```

Pour verifier rapidement depuis PowerShell :

```powershell
Get-ChildItem data\processed
Get-ChildItem outputs\maps
Get-ChildItem outputs\tables
```

---

## 6. Plan de video YouTube

### Episode ou chapitre 1 - Introduction, 2 minutes

Montre le resultat final ou la carte, puis pose les trois questions du projet. Explique que tu vas reconstruire l'analyse depuis les donnees brutes.

Phrase possible :

> « Aujourd'hui, on ne va pas seulement afficher une carte. On va comprendre comment passer de fichiers bruts a des indicateurs qui peuvent aider a orienter une decision. »

### Chapitre 2 - Comprendre les donnees, 5 minutes

Montre le dossier `data/raw`, puis execute le notebook 01. Explique les CSV, GeoJSON et la colonne `geometry`.

### Chapitre 3 - Nettoyer, 10 a 15 minutes

Montre le probleme des encodages, les noms de communes et les coordonnees WKT. Execute le notebook 02 et affiche les compteurs finaux.

### Chapitre 4 - Faire parler la carte, 8 a 10 minutes

Execute le notebook 03. Montre les limites communales, les points, le controle des points hors limites et la carte interactive.

### Chapitre 5 - Comparer correctement, 10 a 15 minutes

Execute le notebook 04. Explique pourquoi un total brut est trompeur et pourquoi on utilise une densite par habitant.

### Chapitre 6 - Prioriser sans surinterpreter, 5 minutes

Explique le score, affiche les communes prioritaires et rappelle qu'il s'agit d'une liste a investiguer, pas d'une preuve de zone blanche.

### Conclusion, 2 minutes

Recapitule :

- les donnees ont ete inspectees ;
- les sources ont ete harmonisees ;
- les points ont ete controles spatialement ;
- les densites ont ete calculees ;
- les limites de l'analyse ont ete explicitees.

---

## 7. Erreurs frequentes et solutions

### `FileNotFoundError`

Cause : le terminal ou le kernel ne travaille pas dans le bon dossier.

Solution : ouvre la racine du projet et verifie `Path.cwd()`.

### `ModuleNotFoundError: geopandas`

Cause : le mauvais kernel est selectionne ou les dependances ne sont pas installees.

Solution : selectionne `.venv`, puis installe les dependances avec `python -m pip install geopandas`.

### `UnicodeDecodeError`

Cause : un CSV n'est pas encode en UTF-8.

Solution : utilise `read_csv_safe`, qui essaie `utf-8-sig` puis `latin1`.

### Erreur Excel `could not read stylesheet`

Cause : la feuille de styles du fichier RGPH est invalide.

Solution : ne remplace pas la lecture XML du notebook 02 par `pd.read_excel` pour ce fichier.

### `NameError: display is not defined`

Cause : le code est lance dans un terminal Python au lieu d'un notebook.

Solution : dans un notebook, `display` existe normalement. Le notebook spatial contient deja un fallback ; dans un script simple, utilise `print` ou importe `display` depuis `IPython.display`.

### Carte vide ou points mal places

Verifie :

1. que les geometries sont bien au format `POINT (longitude latitude)` ;
2. que le CRS est `EPSG:4326` ;
3. que longitude et latitude n'ont pas ete inversees ;
4. que les fichiers de limites utilisent le meme CRS.

### Beaucoup de communes sans population

Cause : les noms ne sont pas ecrits exactement de la meme facon.

Solution : utilise `normalize_key` avant la jointure et inspecte quelques noms qui ne correspondent pas.

---

## 8. Ce qu'il ne faut pas affirmer dans la video

Evite ces formulations :

- « Cette commune est une zone blanche. »
- « Cette region a la meilleure couverture reseau. »
- « Tous les points sont actifs. »
- « Le score prouve ou investir. »

Utilise plutot :

- « Cette commune apparait comme prioritaire dans les donnees disponibles. »
- « Cette region presente la densite de points recenses la plus elevee. »
- « Ce resultat doit etre confronte a la couverture et a la qualite de service. »
- « Le score sert a organiser une investigation complementaire. »

---

## 9. Checklist avant publication

### Code

- [ ] Les quatre notebooks s'executent dans l'ordre.
- [ ] Le kernel utilise le bon environnement Python.
- [ ] Les cellules ne contiennent pas d'erreur.
- [ ] Les sorties generees sont visibles.
- [ ] Les noms de fichiers correspondent au depot.

### Donnees

- [ ] Les sources sont citees dans la description YouTube.
- [ ] La date ou la periode des donnees est indiquee.
- [ ] Les limites des donnees sont expliquees.
- [ ] La couverture reseau n'est pas deduite des seuls points recenses.

### Video

- [ ] Le curseur est visible pendant les manipulations.
- [ ] Les resultats importants sont zoomés a l'ecran.
- [ ] Les chiffres sont lus et interpretes, pas seulement affiches.
- [ ] Les erreurs rencontrees sont expliquees calmement.
- [ ] La conclusion distingue clairement resultat, interpretation et limite.

---

## 10. Resume en une phrase

> On inspecte les sources, on les nettoie, on les place sur la carte, on rapporte l'offre a la population, puis on utilise ces indicateurs pour choisir quelles communes examiner en premier, sans confondre presence recensee et couverture reseau.
