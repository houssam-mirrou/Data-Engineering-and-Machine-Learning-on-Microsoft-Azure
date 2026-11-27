RAPPORT FINAL AZURE — REGENERATION

Livrable : rapport_final_azure_fintech.pdf (15 pages, français, A4).
Preuves : evidence_inventory.md (64 captures visuellement inspectées).
Le PDF inclut 10 captures distinctes, recadrées sans modification des originaux.

Depuis la racine du projet :
  python -m venv /tmp/azure-report-venv
  /tmp/azure-report-venv/bin/python -m pip install -r report/requirements.txt
  /tmp/azure-report-venv/bin/python report/build_inventory.py
  /tmp/azure-report-venv/bin/python report/generate_report.py

La génération a été vérifiée avec Python 3.14.8, ReportLab 5.1.2 et Pillow 13.0.0.
Les polices Noto Sans Regular/Bold et Noto Sans Mono sont chargées depuis
/usr/share/fonts/noto/. Adapter ces trois chemins si nécessaire sur une autre machine.
Les captures doivent rester dans Screenshots/, à côté du dossier report/.
generate_report.py n'exécute pas les scripts ML et ne contacte aucun service Azure.

Contrôles et rendu (outils système Poppler et qpdf) :
  qpdf --check report/rapport_final_azure_fintech.pdf
  pdfinfo report/rapport_final_azure_fintech.pdf
  pdffonts report/rapport_final_azure_fintech.pdf
  pdftotext -layout report/rapport_final_azure_fintech.pdf report/rapport_final_azure_fintech.txt
  mkdir -p report/rendered
  pdftoppm -scale-to 1400 -png report/rapport_final_azure_fintech.pdf report/rendered/page

Le dossier rendered/ conserve une image de chaque page pour vérification visuelle.
figure_manifest.json associe chaque figure à son original, son recadrage et sa page.
evidence_manifest.json conserve les observations et empreintes SHA-256 des originaux.

Limites principales explicitement documentées :
- Pas de CSV source, de métriques JSON exportées ou de modèle binaire fourni.
- Séparation temporelle Classic et train_flag non auditables intégralement.
- Repli Blob et incidents d'authentification décrits dans les notes, sans preuve locale.
- Modèle enregistré et job d'inférence terminé ; aucun endpoint API démontré.
- Configurations matérielles et dates incohérentes du brief signalées sans les réécrire.

Les références externes Microsoft et CNIL sont cliquables dans le PDF.
L'inventaire a été constitué avant la rédaction du rapport ; build_inventory.py
permet de reproduire les notes d'inspection, sans prétendre inspecter à nouveau les images.
