"""Evidence notes recorded after individual visual review of all 64 originals."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
NOTES = [
('Azure Resource Manager','HMirrou ; North Europe ; groupe vide à cet instant ; 24/11/2026 visible.','Architecture'),
('Azure IAM','Houssam MIRROU ; une attribution de rôle au périmètre HMirrou ; libellé Apprenant-DataML-Form… tronqué ; aucune attribution refusée. Ne démontre pas le moindre privilège.','Gouvernance'),
('Azure Storage','Formulaire : stforecastbrief1 ; HMirrou ; North Europe. Configuration, pas encore création.','Stockage'),
('Azure Storage','Formulaire : Standard ; Big Data Analytics ; réplication LRS.','Stockage'),
('Azure Storage','Récapitulatif : HNS activé ; LRS ; Hot ; SFTP/NFS v3 désactivés.','Stockage'),
('Azure Resource Manager','Déploiement de stforecastbrief1 en cours ; opération Accepted ; pas un succès final.','Architecture'),
('Azure Storage','Provisioning Succeeded ; StorageV2 ; North Europe ; LRS ; HNS activé ; anonyme désactivé ; soft delete blobs/conteneurs 7 jours ; versioning désactivé ; TLS 1.2 ; secure transfer activé ; clés et réseau public tous réseaux activés ; 0 private endpoints ; infrastructure encryption désactivé.','Stockage ; Gouvernance'),
('Azure Storage','Conteneur consumption créé ; accès Private ; également $logs.','Stockage'),
('Azure Storage','consumption/raw/2026/11/24 ; répertoire vide ; méthode Access key.','Stockage'),
('Azure Data Factory','Récapitulatif : adf-forecastbrief1 ; V2 ; North Europe ; public endpoint.','Ingestion'),
('Azure Resource Manager','Déploiement CreateDataFactory terminé avec succès dans HMirrou.','Ingestion'),
('Azure Resource Manager','Deux déploiements réussis ; liste affichée : un compte de stockage. Liste partielle/temporelle, ne prouve pas absence ADF.','Architecture'),
('Azure Data Factory','Formulaire : adf-forecastbrief1 ; HMirrou ; North Europe ; V2.','Ingestion'),
('Azure Data Factory Studio','Accueil adf-forecastbrief1 accessible ; bannière de configuration Git ; aucune preuve de dépôt lié.','Ingestion ; Reproductibilité'),
('Azure Data Factory','ls_adls_forecast dans les linked services ; type Azure Data Lake Storage Gen2.','Ingestion'),
('Azure Data Factory','ls_adls_forecast ; AutoResolveIntegrationRuntime ; Account key ; stforecastbrief1 ; Connection successful.','Ingestion ; Gouvernance'),
('Azure Storage','consumption/source/pjme hourly.csv ; block blob ; 3.88 MiB ; 24/11/2026 16:37:13 ; Access key.','Ingestion'),
('Azure Data Factory','ds_source_csv ; consumption/source/pjme hourly.csv ; première ligne en-tête ; import du schéma depuis stockage.','Ingestion'),
('Azure Data Factory','Aperçu réel : Datetime et PJME_MW ; heures du 31/12/2002 ; exemples 26498.0 et 25147.0 ; infobulle masque une cellule. Ne prouve pas contrôle exhaustif.','Ingestion ; EDA'),
('Azure Data Factory','ds_source_csv ; DelimitedText ; virgule ; UTF-8 ; sans compression ; en-tête activé.','Ingestion'),
('Azure Data Factory','ds_raw_csv vers raw/2026/11/24 ; message Failed partiellement coupé près de l’aperçu ; cause non lisible.','Difficultés'),
('Azure Data Factory','Publishing completed ; ds_raw_csv publié ; message Failed encore présent pour aperçu destination. Publication distincte de l’exécution.','Difficultés'),
('Azure Data Factory','pipeline1 ; copy_consumption_csv ; source ds_source_csv ; pas de résultat d’exécution.','Ingestion'),
('Azure Data Factory','Pipeline renommé pl_ingest_consumption ; sink ds_raw_csv ; extension .txt visible.','Ingestion ; Difficultés'),
('Azure Data Factory','pl_ingest_consumption ; activité copy_consumption_csv ; timeout 12 h ; retry 0 ; secure input/output non cochés ; configuration.','Ingestion'),
('Azure Data Factory','Mapping explicite Datetime → Datetime et PJME_MW → PJME_MW ; deux types String.','Ingestion'),
('Azure Data Factory','Activité Succeeded ; 19 s ; démarrage 25/11/2026 09:51:33 ; pipeline encore In progress ; run 766baa00-cadd-4f75-81db-ecd5cce13f1b.','Ingestion'),
('Azure Storage','raw/2026/11/25/pjme hourly.txt ; 4.57 MiB ; 09:51:49. Sortie texte, pas copie binaire identique démontrée.','Stockage ; Difficultés'),
('Azure Data Factory','Pipeline et activité Succeeded ; 17 s ; démarrage 09:59:26 le 25/11/2026 ; run 8748d7a7-51ac-43ad-81fe-6085a3b4ea2f.','Ingestion'),
('Azure Storage','raw/2026/11/25 contient pjme hourly.csv et pjme hourly.txt ; chacun 4.57 MiB ; CSV modifié 09:59:40.','Stockage'),
('Azure ML','Création ml-forecastbrief1 ; North Europe ; ressources associées proposées ; pas encore succès.','Architecture'),
('Azure ML','ml-forecastbrief1 ; Provisioning State Succeeded ; North Europe ; stockage associé distinct de stforecastbrief1 ; Key Vault et Application Insights visibles.','Architecture'),
('Azure ML','Formulaire ds_adls_forecast ; Azure Data Lake Storage Gen2 ; stforecastbrief1 ; consumption ; sauvegarde credentials et identité workspace pour aperçu désactivées.','Stockage'),
('Azure ML','Create success ; ds_adls_forecast créé ; type Azure Data Lake Storage Gen2 ; auteur Houssam MIRROU. Création ne prouve pas accès aux octets.','Stockage'),
('Azure ML Compute','CPU Dedicated ; North Europe ; sélection Standard_DS11_v2 ; 2 cores ; 14 GB RAM ; 28 GB stockage selon interface.','Compute'),
('Azure ML Compute','cpu-forecast ; Standard_DS11_v2 ; min 0 ; max 1 ; scale down 120 s ; SSH désactivé ; formulaire.','Compute'),
('Azure ML Data','Récapitulatif pjme_consumption ; uri_file ; datastore ds_adls_forecast ; raw/2026/11/25/pjme hourly.csv.','Stockage'),
('Azure ML Data','pjme_consumption version 1 créé ; ds_adls_forecast ; URI dfs.core.windows.net ; Houssam MIRROU ; 25/11/2026 11:46. Ne démontre pas connexion Blob finale.','Stockage ; Traçabilité'),
('Azure ML Designer','Canvas vide ; No data assets found. Constat à cet instant, sans cause prouvée.','Difficultés'),
('Azure ML Designer','pl_pjme_forecasting ; pjme_consumption v1 désormais visible dans bibliothèque ; canvas vide.','Difficultés'),
('Azure ML Designer','pjme_consumption v1 ajouté au canvas ; bibliothèque composants ; pas d’exécution.','Architecture'),
('Azure ML Designer','Trois composants PJME Prepare, Train random forest, Evaluate présents et enregistrés en v1 ; placés mais entrées rouges non reliées ; aucune exécution démontrée.','Annexes ; Reproductibilité'),
('Azure ML Classic Designer','pl_pjme_forecasting_classic ; pjme_consumption2 v1 connecté à Summarize Data.','EDA'),
('Azure ML Classic Designer','Validation graphe positive ; revue job pjme-eda-v1 ; expérience pjme-forecasting ; compute cpu-forecast ; continue on step failure True.','EDA'),
('Azure ML Classic Designer','Soumission pjme-eda-v1 réussie ; job Running ; pas encore Completed.','EDA'),
('Azure ML Jobs','pjme-eda-v1 Running ; Summarize Data en attente ; run 6df683b2-cc3c-4344-bfc5-0475e081d143.','EDA'),
('Azure ML Compute','cpu-forecast provisionné ; allocation Succeeded (1 node), Preparing ; DS11_v2 2 cores 14 GB ; Linux Dedicated ; minimum 0 visible.','Compute'),
('Azure ML Visualisation','Sortie Summarize Data : 2 lignes de statistiques, 23 colonnes ; chaque variable Count 145366 ; Datetime unique 145362 ; manquants 0 chacun ; PJME_MW min 14544.0, max 62009.0, moyenne 32080.222830648156, médiane 31421.0 ; dates min 2002-01-01 01:00:00+00:00 et max 2018-08-03 00:00:00+00:00. Provenance run différent de l’EDA initiale : c7b7d460-a4b2-4eb2-93c9-547fbb5a5448.','EDA'),
('Azure ML Classic Designer','pjme_consumption_3 v1 ; branches Summarize Data et Clean Missing Data ; avertissement configuration sur nettoyage ; pas de paramètres détaillés.','Prétraitement'),
('Azure ML Classic Designer','Split Data vers deux Select Columns ; Decision Forest Regression → Train Model → Score Model → Evaluate Model ; câblage visible ; configuration split non affichée.','Séparation ; Entraînement'),
('Azure ML Jobs','pl_pjme_forecasting_classic Running ; Summarize, Clean Missing, Remove Duplicate, deux Edit Metadata et Python avec coches vertes/cache ; source pjme_consumption_3 ; run f9afd8ab-33a6-48ac-bbb0-432bac286e56.','Prétraitement'),
('Azure ML Jobs','Même run f9afd8ab… ; Python et forêt verts ; Split Data en exécution ; Train/Score/Evaluate pas encore terminés dans cette image.','Entraînement'),
('Azure ML Visualisation','Évaluation liée au run f9afd8ab… ; MAE 3177.774545 ; RMSE 4251.194918 ; RSE 0.429223 ; RAE 0.630538 ; R² 0.570777 ; 1 ligne, 5 colonnes.','Évaluation'),
('Azure ML Visualisation','Même run f9afd8ab… ; Scored_dataset : 29074 lignes, 8 colonnes ; PJME_MW, Hour, DayOfWeek, Month, Quarter, Year, DayOfYear, Scored Labels ; valeurs calendrier et prédictions réelles.','Features ; Évaluation'),
('Azure ML Models','forecastingmodelv1 version 1 ; CUSTOM ; expérience train_model_experiment ; créé 25/11/2026 17:15 ; run enfant 9fd9598e-62fa-4638-9d3a-e8e… tronqué. Enregistrement confirmé, liaison exacte métriques/modèle non exportée.','Enregistrement'),
('Azure ML Designer','Pipeline pl_pjme_forecasting_classic-real time inference généré ; transformation TD ; pjme_consumption_3 ; Apply Transformation ; Remove Duplicate ; Edit Metadata ; état édition.','Inférence'),
('Azure ML Designer','Même brouillon inférence ; Python ; sélection colonnes ; artefact MD-…Train_M… v1 connecté à Score Model.','Inférence'),
('Azure ML Designer','Brouillon inférence ; Score Model vers Web Service Output et Evaluate Model ; pas de déploiement démontré.','Inférence'),
('Azure ML Designer','Autre brouillon même nom inférence ; haut du graphe transformation/nettoyage ; pas de statut job.','Inférence'),
('Azure ML Designer','Même autre brouillon ; bas du graphe Score/Output/Evaluate ; pas d’entrée Web Service Input visible.','Inférence'),
('Azure ML Jobs','Workspace ml-forecastbrief-1-2 ; experiment_2 ; pipeline inférence Completed ; transformation/nettoyage/métadonnées/Python verts ; run 67d0f4cf-1186-47d3-a67a-c1cd61a30b8c. Prouve changement workspace, pas sa cause.','Inférence ; Difficultés'),
('Azure ML Jobs','Même run 67d0f4cf… Completed ; Select Columns, Score Model et Evaluate Model verts ; Web Service Output ; aucune métrique chiffrée ni réponse API.','Inférence'),
('Azure ML Jobs','Même run 67d0f4cf… et workspace ; nouvelle capture du haut à 13:36 ; aucune nouvelle exécution démontrée.','Inférence'),
('Azure ML Jobs','Même run 67d0f4cf… Completed ; bas du graphe à 13:36 ; doublon utile pour lecture, pas un second succès indépendant.','Inférence'),
]

def main():
    paths = sorted((ROOT/'Screenshots').glob('*.png'))
    assert len(paths) == len(NOTES) == 64
    rows = []
    lines = ['# Inventaire des preuves — inspection visuelle préalable', '',
    'Les 64 images originales ont été ouvertes individuellement avec view_image avant toute rédaction du rapport. Aucun OCR utilisé. Les identifiants E01–E64 suivent le tri des chemins. Une confiance élevée qualifie la lecture de l’écran et non la complétude de l’implémentation.', '',
    '| Screenshot | Azure service | Visible evidence | Relevant report section | Confidence |',
    '|---|---|---|---|---|']
    for i, (p, (service, note, section)) in enumerate(zip(paths,NOTES),1):
        eid = f'E{i:02d}'
        confidence = 'Élevée' if i not in [2,12,21,22,39,55] else 'Élevée sur le visible ; limite explicitée'
        lines.append(f'| {eid} — [{p.name}](../Screenshots/{p.name.replace(" ", "%20")}) | {service} | {note} | {section} | {confidence} |')
        rows.append(dict(id=eid,file=str(p.relative_to(ROOT)),service=service,evidence=note,section=section,confidence=confidence,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    lines += ['', '## Chronologie et rapprochements', '',
    '- 24/11/2026 : groupe, stockage HNS, conteneur privé, ADF et service lié ADLS par clé ; dépôt source de 3,88 MiB. Les dates sont lues sur les interfaces ; le fuseau des captures n’est pas établi.',
    '- 25/11 matin : sortie .txt puis .csv de 4,57 MiB dans raw/2026/11/25 ; second pipeline ADF Succeeded. Workspace initial et datastore ADLS enregistrés ; cluster DS11_v2 0–1 nœud.',
    '- 25/11 midi : composants Python enregistrés/placés, sans exécution démontrée. L’archive contient un avertissement explicite de non-exécution.',
    '- 25/11 après-midi : Designer Classic avec plusieurs assets (pjme_consumption2 puis pjme_consumption_3) ; statistiques E48 et évaluation E53 proviennent de runs distincts. E51–E54 se rattachent à f9afd8ab… ; E55 montre un run enfant tronqué.',
    '- 25/11 fin de journée : enregistrement du modèle et création de brouillons d’inférence. 26/11 : job d’inférence Completed dans ml-forecastbrief-1-2 ; E61–E64 sont des vues d’un seul run.', '',
    '## Sources locales inspectées', '',
    '- Trois scripts et trois YAML sous Script/ ; contenus lus intégralement. L’archive pjme_azure_components.zip contient les mêmes six fichiers et README.txt. Le README précise que le code n’a pas été exécuté dans Azure. E42 prouve l’existence de composants enregistrés mais leurs noms techniques diffèrent de certains noms YAML ; identité exacte des versions non certifiée.',
    '- prepare.py : parsing, suppression des valeurs manquantes, tri, dédoublonnage par timestamp, six features et coupe iloc à 80 %. Les effectifs de cette variante ne doivent pas être confondus avec ceux du Designer Classic.',
    '- train.py : RandomForestRegressor (60 arbres, profondeur 16, feuille min 5, n_jobs 2, random_state 42). Ces paramètres ne sont pas ceux de Decision Forest Regression démontrés dans Azure.',
    '- evaluate.py : MAE, RMSE, R² et MAE baseline moyenne, exports prévus. Aucun audit.json, metrics.json, predictions.csv, CSV source, modèle binaire, journal ou notebook fourni dans le dossier.',
    '- Cahier des charges disponible uniquement dans le texte joint par l’utilisateur ; pas de document d’énoncé indépendant dans le projet.', '',
    '## Écarts et absences de preuves à conserver dans le rapport', '',
    '- train_flag et expression Split Data : décrits par les notes utilisateur mais non visibles dans les captures ; intention temporelle corroborée par le script local et l’aperçu test, sans audit complet du run Classic.',
    '- Aucune capture d’erreur authentification ADLS, du datastore Blob réussi, du soft-delete workspace ou d’erreur syntaxe Split Data. Ne pas raconter ces incidents comme faits vérifiés.',
    '- Changement workspace initial → ml-forecastbrief-1-2 visible ; suppression/recréation et équivalence des configurations non prouvées.',
    '- Aucun endpoint déployé, URL de scoring ou appel API de test. Completed du job d’inférence ne prouve pas une API temps réel.',
    '- RGPD : paramètres techniques démontrés seulement ; conformité juridique non établie.',
    '- StandardDS2v3 / 2 vCPU / 14 GB du brief incohérent : Standard_D2s_v3 officiel = 2 vCPU / 8 GiB ; observé Standard_DS11_v2 = 2 vCPU / 14 GiB. Sources Microsoft consultées le 27/11/2026 : https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/general-purpose/dsv3-series et https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/memory-optimized/dv2-dsv2-series-memory.',
    '- Période du brief conservée : 23/11/2025 au 27/11/2026 à 17:30 ; écart d’année apparent avec une courte séquence de captures du 24 au 26/11/2026, sans correction arbitraire.', '',
    '## Sélection éditoriale', '',
    'Le PDF sélectionne les preuves lisibles et non redondantes ; le manifeste des figures est produit par generate_report.py. Les recadrages retirent uniquement des zones de navigateur, menus ou espaces inutiles ; les originaux restent inchangés.']
    (ROOT/'report/evidence_inventory.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    (ROOT/'report/evidence_manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

if __name__ == '__main__':
    main()
