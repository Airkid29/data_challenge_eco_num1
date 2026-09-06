# Togo Connect — tableau de bord Python

## Lancement

Depuis la racine du challenge :

```powershell
pip install -r dashboard/requirements.txt
python dashboard/app.py
```

Ouvrir ensuite `http://127.0.0.1:8050`.

## Contenu

- carte à couches des agences Moov, Togocom, Télécom, CANAL+, data centers et points Mobile Money ;
- filtres par région et type de service ;
- indicateurs, répartitions régionales et liste de communes à investiguer en priorité ;
- avertissement explicite sur les variables absentes (population/lotissements et couverture cellulaire).

Le « score de priorité » est un signal de faible desserte fondé uniquement sur les points recensés. Il ne constitue pas une recommandation d’investissement sans jointure avec la population, la couverture mobile et les contraintes terrain.
