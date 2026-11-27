# Prévision de la consommation électrique sur Microsoft Azure

Projet de **Data Engineering et de Machine Learning** réalisé par **Houssam MIRROU** dans un contexte de formation Simplon.

L’objectif est de construire une chaîne allant de l’ingestion d’un fichier de consommation électrique horaire à la préparation des données, l’entraînement d’un modèle de régression et son évaluation dans Azure Machine Learning.

Ce dépôt rassemble les preuves de réalisation et un rapport technique en français. Il documente les résultats observés ainsi que les étapes restant à valider avant une utilisation en production.

## Livrables

- [Rapport technique final — PDF, 15 pages](report/rapport_final_azure_fintech.pdf).
- [Inventaire des 64 captures inspectées](report/evidence_inventory.md).
- [Générateur du rapport](report/generate_report.py) et [instructions de régénération](report/README.txt).
- [Compte rendu de vérification du PDF](report/verification.txt).

Le rapport intègre 10 captures distinctes. Ses 15 pages ont été rendues en images et vérifiées visuellement.

## Architecture et périmètre

Le parcours documenté s’appuie sur les services suivants :

| Service | Rôle dans le projet |
|---|---|
| Azure Data Factory | Copier le fichier source vers une zone de stockage datée. |
| Azure Storage avec espace de noms hiérarchique | Organiser les fichiers dans un conteneur et des répertoires `source/` et `raw/`. |
| Azure Machine Learning | Enregistrer les données, explorer leur qualité et assembler les traitements dans Designer. |
| Azure ML Compute | Exécuter les traitements sur un cluster CPU avec autoscaling. |
| Azure ML Classic Designer | Préparer les variables, entraîner une forêt de régression, produire des prédictions et les évaluer. |

Le fichier source est d’abord déposé dans Azure Storage. ADF le copie ensuite vers `raw/2026/11/25/`. Les captures ML montrent la préparation, l’entraînement et l’évaluation, puis un job d’inférence dans un second workspace.

La filiation complète entre les différents assets ML et les deux workspaces reste à documenter. Aucun déclenchement automatique de ML depuis ADF n’est démontré.

### Ressources observées

| Ressource | Nom ou configuration |
|---|---|
| Groupe de ressources | `HMirrou` |
| Région initiale | `North Europe` |
| Compte de stockage | `stforecastbrief1` |
| Conteneur | `consumption` |
| Data Factory | `adf-forecastbrief1` |
| Pipeline d’ingestion | `pl_ingest_consumption` |
| Activité de copie | `copy_consumption_csv` |
| Service lié ADF | `ls_adls_forecast` — ADLS Gen2 |
| Workspace ML initial | `ml-forecastbrief1` |
| Datastore ML initial enregistré | `ds_adls_forecast` — ADLS Gen2 |
| Cluster CPU | `cpu-forecast` — `Standard_DS11_v2` |
| Autoscaling configuré | Minimum 0, maximum 1 nœud ; réduction après 120 s d’inactivité |
| Pipeline Classic | `pl_pjme_forecasting_classic` |
| Modèle enregistré | `forecastingmodelv1`, version 1, type `CUSTOM` |
| Workspace du job d’inférence ultérieur | `ml-forecastbrief-1-2` |

La VM visible est `Standard_DS11_v2`, avec 2 vCPU et 14 GiB de mémoire selon la documentation Microsoft. Le brief mentionne « StandardDS2v3 » avec 14 GB : cette désignation est incohérente avec `Standard_D2s_v3`, qui dispose de 8 GiB. Voir les fiches [DSv2](https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/memory-optimized/dv2-dsv2-series-memory) et [Dsv3](https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/general-purpose/dsv3-series), vérifiées lors de la préparation du rapport.

## Données et qualité

Le fichier observé dans Azure est `pjme hourly.csv`, composé de deux colonnes principales :

| Colonne | Signification |
|---|---|
| `Datetime` | Horodatage de l’observation horaire. |
| `PJME_MW` | Puissance électrique en mégawatts ; cible de la régression. |

La sortie de **Summarize Data** indique :

- **145 366 observations** et **145 362 horodatages distincts**.
- **0 valeur manquante déclarée** pour chacune des deux colonnes.
- Une moyenne de **32 080,222830648156 MW**, une médiane de **31 421,0 MW** et des valeurs comprises entre **14 544,0 et 62 009,0 MW**.
- Des bornes temporelles affichées du `2002-01-01 01:00:00+00:00` au `2018-08-03 00:00:00+00:00` ; le fuseau de collecte d’origine n’est pas établi.

L’écart de quatre occurrences entre l’effectif et les horodatages distincts ne prouve pas l’existence de quatre lignes identiques. La continuité horaire, les horodatages répétés et les valeurs atypiques nécessitent des contrôles complémentaires.

Le dépôt ADF utilise le format **DelimitedText** : virgule, UTF-8 et première ligne d’en-tête. Le source apparaît à 3,88 MiB et les sorties à 4,57 MiB. La copie peut donc correspondre à une nouvelle sérialisation du contenu ; la conservation des octets d’origine n’a pas été vérifiée.

## Workflow Machine Learning

Le graphe Classic documenté comprend :

1. **Summarize Data** pour l’exploration.
2. **Clean Missing Data**, **Remove Duplicate Rows** et deux **Edit Metadata** pour le prétraitement.
3. **Execute Python Script** pour les variables calendaires.
4. **Split Data** et deux **Select Columns in Dataset** pour préparer les branches d’apprentissage et de test.
5. **Decision Forest Regression**, **Train Model**, **Score Model** et **Evaluate Model**.

Les six variables calendaires visibles dans les données scorées sont `Hour`, `DayOfWeek`, `Month`, `Quarter`, `Year` et `DayOfYear`.

### Séparation temporelle

Le protocole attendu réserve les 80 % les plus anciens à l’apprentissage et les 20 % les plus récents au test. Les notes de réalisation décrivent un indicateur `train_flag`, mais sa construction et l’expression de **Split Data** ne sont pas visibles dans les captures.

Les **29 074 observations de test** sont compatibles avec une proportion d’environ 20 %, sans suffire à prouver la chronologie. L’export des bornes train/test et la vérification de `max(train.Datetime) < min(test.Datetime)` restent nécessaires pour auditer le run Classic.

### Résultats vérifiés

Les valeurs suivantes proviennent de la capture d’évaluation du run Classic du 25 novembre 2026 :

| Indicateur | Valeur visible |
|---|---:|
| MAE | 3 177,774545 MW |
| RMSE | 4 251,194918 MW |
| R² | 0,570777 |
| Observations de test | 29 074 |

Ces métriques indiquent une **performance explicative modérée**. Elles ne constituent pas une validation de précision opérationnelle et ne sont pas attribuées au job d’inférence ultérieur. Aucun résultat chiffré de baseline n’est fourni.

Preuves : [métriques d’évaluation](Screenshots/Screenshot%202026-11-25%20171054.png) et [données scorées](Screenshots/Screenshot%202026-11-25%20171108.png).

## État de réalisation

| Étape | État documenté |
|---|---|
| Copie ADF | Pipeline et activité `Succeeded` ; activité de 17 s sur le second essai documenté. |
| Stockage daté | Présence de sorties `.txt` puis `.csv` dans `raw/2026/11/25/`. |
| Préparation et régression Classic | Graphe et sorties de prédiction/évaluation disponibles. |
| Enregistrement du modèle | `forecastingmodelv1:1` visible dans Models. |
| Création du pipeline d’inférence | Graphe généré dans Designer. |
| Exécution de l’inférence | Job `Completed` dans `ml-forecastbrief-1-2` le 26 novembre. |
| Endpoint temps réel | Aucun déploiement, URL de scoring ou appel API réussi démontré. |
| Orchestration ADF vers ML | Non démontrée. |

La capture d’un job d’inférence terminé prouve une exécution dans Azure ML, sans établir l’existence d’un service accessible en temps réel. La correspondance exacte entre le modèle enregistré, le run évalué et les artefacts du second workspace doit également être conservée dans des exports de métadonnées.

## Structure actuelle du dépôt

```text
.
├── README.md
├── Screenshots/                         # 64 captures Azure originales
└── report/
    ├── rapport_final_azure_fintech.pdf   # Rapport technique final
    ├── rapport_final_azure_fintech.txt   # Texte extrait du PDF
    ├── evidence_inventory.md            # Observations et limites par capture
    ├── evidence_manifest.json           # Inventaire avec empreintes SHA-256
    ├── figure_manifest.json             # Sources, pages et recadrages des figures
    ├── build_inventory.py               # Reconstitution des notes d’inspection
    ├── generate_report.py               # Génération du PDF
    ├── requirements.txt                 # Dépendances du générateur
    ├── README.txt                       # Instructions détaillées
    ├── verification.txt                 # Contrôles effectués
    └── rendered/                        # Rendus PNG des 15 pages
```

### Variante Python décrite dans le rapport

Lors de l’analyse initiale, trois composants Python/YAML de préparation, d’entraînement et d’évaluation étaient disponibles sous `Script/`, avec l’archive `pjme_azure_components.zip`. **Ces fichiers ne sont plus présents dans le dossier actuel.** Leur fonctionnement est décrit dans le rapport et l’inventaire.

Cette variante utilisait `RandomForestRegressor` avec 60 arbres, une profondeur maximale de 16, une taille minimale de feuille de 5 et `random_state=42`. Son exécution réussie n’était pas démontrée. Ces paramètres ne doivent pas être attribués au modèle **Decision Forest Regression** évalué dans Classic Designer.

Le dépôt actuel ne contient ni CSV source, ni modèle binaire, ni exports ML `audit.json`, `metrics.json` ou `predictions.csv`. Il permet de régénérer le rapport ; il ne permet pas de reproduire intégralement l’apprentissage à partir des seuls fichiers présents.

## Régénérer le rapport PDF

Depuis la racine du dépôt, créer un environnement Python et installer les dépendances du rapport :

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r report/requirements.txt
python report/build_inventory.py
python report/generate_report.py
```

Le PDF est généré dans `report/rapport_final_azure_fintech.pdf`. Les scripts ne contactent pas Azure et n’exécutent aucun entraînement ML.

La génération a été vérifiée avec Python 3.14.8, ReportLab 5.1.2 et Pillow 13.0.0. Le générateur charge **Noto Sans Regular/Bold** et **Noto Sans Mono** depuis `/usr/share/fonts/noto/` : adapter les chemins de polices si nécessaire sur une autre machine. Sous Windows, l’activation du venv et ces chemins doivent également être adaptés.

`build_inventory.py` restitue les notes d’inspection déjà rédigées. Il ne réalise pas une nouvelle inspection visuelle des captures.

Pour contrôler et rendre le PDF avec **qpdf** et **Poppler** installés sur le système :

```bash
qpdf --check report/rapport_final_azure_fintech.pdf
pdfinfo report/rapport_final_azure_fintech.pdf
mkdir -p report/rendered
pdftoppm -scale-to 1400 -png report/rapport_final_azure_fintech.pdf report/rendered/page
```

Ouvrir ensuite les images produites pour vérifier la lisibilité des figures, les accents, les marges et l’absence de chevauchements.

## Gouvernance et sécurité

Les captures montrent un conteneur privé, l’accès anonyme aux blobs désactivé, le transfert sécurisé activé, TLS 1.2 minimum et une suppression réversible de sept jours pour les blobs et conteneurs.

Elles montrent aussi une authentification ADF par clé de compte, un accès réseau public depuis tous les réseaux, aucun private endpoint et un versioning désactivé. L’usage d’identités managées, le moindre privilège, le filtrage réseau, la rotation des secrets et les tests de restauration sont des améliorations à documenter et à valider.

Aucune conformité RGPD complète n’est revendiquée. Les données visibles sont agrégées, mais les captures contiennent notamment le nom de l’auteur et des identifiants de compte Azure.

## Limites et prochaines étapes

- Exporter le pipeline Classic, les scripts embarqués, ses paramètres et l’audit de séparation temporelle.
- Documenter la filiation des assets et le datastore effectivement utilisé à chaque étape. Le repli vers Blob Storage mentionné dans les notes n’est pas confirmé par les captures disponibles.
- Comparer le modèle à des références J−1/J−7, puis explorer les variables retardées, les statistiques glissantes, la météo et les jours fériés avec une validation temporelle adaptée.
- Valider l’inférence sur des entrées futures sans cible, puis déployer et tester un endpoint si un service temps réel est requis.
- Automatiser l’enchaînement ingestion/ML et ajouter des contrôles de qualité et de supervision.

Le brief indique une période du **23/11/2025 au 27/11/2026 à 17:30**, alors que les captures documentent les **24–26 novembre 2026**. Cet écart d’année apparent est conservé dans le rapport sans correction arbitraire.

Pour les preuves détaillées, leurs identifiants et leurs limites, consulter l’[inventaire](report/evidence_inventory.md).
