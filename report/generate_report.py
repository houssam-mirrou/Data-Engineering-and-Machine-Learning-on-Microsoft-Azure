"""Generate the French A4 report from the reviewed evidence inventory.

Run: python report/generate_report.py
Dependencies: reportlab, Pillow. No Azure access or model execution required.
All original screenshots remain unchanged; figure crops are explicit below.
"""
from pathlib import Path
from xml.sax.saxutils import escape
import json

from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'report'
W, H = 595.276, 841.89
M = 43
CW = W - 2*M
NAVY = HexColor('#102A43')
BLUE = HexColor('#0078D4')
TEXT = HexColor('#243B53')
GRAY = HexColor('#627D98')
PALE = HexColor('#EDF5FC')
LINE = HexColor('#D9E2EC')

for name, path in [
    ('Noto','/usr/share/fonts/noto/NotoSans-Regular.ttf'),
    ('NotoBold','/usr/share/fonts/noto/NotoSans-Bold.ttf'),
    ('Mono','/usr/share/fonts/noto/NotoSansMono-Regular.ttf')]:
    pdfmetrics.registerFont(TTFont(name,path))
pdfmetrics.registerFontFamily('Noto',normal='Noto',bold='NotoBold',italic='Noto',boldItalic='NotoBold')

STYLES = {
    'body': ParagraphStyle('body',fontName='Noto',fontSize=10.1,leading=15,textColor=TEXT,spaceAfter=8),
    'small': ParagraphStyle('small',fontName='Noto',fontSize=8.1,leading=11.5,textColor=GRAY,spaceAfter=6),
    'caption': ParagraphStyle('caption',fontName='Noto',fontSize=8,leading=11,textColor=GRAY,spaceAfter=10),
    'h2': ParagraphStyle('h2',fontName='NotoBold',fontSize=12,leading=16,textColor=NAVY,spaceAfter=7),
    'table': ParagraphStyle('table',fontName='Noto',fontSize=8.5,leading=12,textColor=TEXT),
    'tablehead': ParagraphStyle('tablehead',fontName='NotoBold',fontSize=8.5,leading=12,textColor=white),
    'code': ParagraphStyle('code',fontName='Mono',fontSize=7.8,leading=11,textColor=TEXT),
}

SOURCES = {
    'DSv3': 'https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/general-purpose/dsv3-series',
    'DSv2': 'https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/memory-optimized/dv2-dsv2-series-memory',
    'Split Data': 'https://learn.microsoft.com/en-us/azure/machine-learning/component-reference/split-data?view=azureml-api-2',
    'CNIL': 'https://www.cnil.fr/fr/comprendre-le-rgpd/les-six-grands-principes-du-rgpd',
}


class Report:
    def __init__(self):
        self.c = canvas.Canvas(str(OUT/'rapport_final_azure_fintech.pdf'),pagesize=(W,H),pageCompression=1)
        self.c.setTitle('Pipeline Azure de prévision de la consommation électrique — Rapport technique')
        self.c.setAuthor('Houssam MIRROU')
        self.c.setSubject('Data Engineering et Machine Learning — étude fondée sur les preuves du projet')
        self.page = 0
        self.y = 0
        self.figures = []
        self.evidence = json.loads((OUT/'evidence_manifest.json').read_text())
        self.toc = []

    def check(self, height):
        if self.y-height < 50:
            raise ValueError(f'Overflow page {self.page}: y={self.y:.1f}, need={height:.1f}')

    def new(self, label, title):
        if self.page:
            self.c.showPage()
        self.page += 1
        c = self.c
        c.setFillColor(BLUE)
        c.rect(0,H-7,W,7,fill=1,stroke=0)
        c.setFont('NotoBold',8)
        c.drawString(M,H-35,'AZURE  /  DATA ENGINEERING & MACHINE LEARNING')
        c.setFillColor(GRAY)
        c.setFont('Noto',8)
        c.drawRightString(W-M,H-35,'Houssam MIRROU · 27.11.2026')
        c.setStrokeColor(LINE)
        c.line(M,43,W-M,43)
        c.setFont('Noto',7.5)
        c.drawString(M,28,'PJME · Rapport technique fondé sur les pièces du projet')
        c.drawRightString(W-M,28,f'{self.page:02d} / 15')
        self.y = H-72
        if title:
            self.para(label.upper(),'small')
            self.para(title,'h2',size=21,leading=26)
            self.y -= 9
            key = f'page-{self.page}'
            c.bookmarkPage(key)
            c.addOutlineEntry(title,key,0,False)
            self.toc.append((title,self.page))

    def para(self,text,style='body',size=None,leading=None):
        s = STYLES[style]
        if size:
            s = ParagraphStyle('override',parent=s,fontSize=size,leading=leading or size*1.4)
        p = Paragraph(text,s)
        _,h = p.wrap(CW,1000)
        gap = s.spaceAfter
        self.check(h+gap)
        p.drawOn(self.c,M,self.y-h)
        self.y -= h+gap

    def sub(self,title):
        self.y -= 4
        self.para(title,'h2')

    def box(self,title,text):
        p = Paragraph(f'<b>{title}</b><br/>{text}',STYLES['body'])
        _,h = p.wrap(CW-26,1000)
        self.check(h+28)
        self.c.setFillColor(PALE)
        self.c.roundRect(M,self.y-h-18,CW,h+18,6,fill=1,stroke=0)
        self.c.setFillColor(BLUE)
        self.c.rect(M,self.y-h-18,3,h+18,fill=1,stroke=0)
        p.drawOn(self.c,M+13,self.y-h-9)
        self.y -= h+28

    def table(self,headers,rows,widths=None):
        widths = widths or [CW/len(headers)]*len(headers)
        data = [[Paragraph(str(x),STYLES['tablehead']) for x in headers]]
        data += [[Paragraph(str(x),STYLES['table']) for x in row] for row in rows]
        t = Table(data,colWidths=widths,hAlign='LEFT')
        t.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),NAVY),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[white,PALE]),
            ('VALIGN',(0,0),(-1,-1),'TOP'),
            ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
            ('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),
            ('LINEBELOW',(0,-1),(-1,-1),0.4,LINE),
        ]))
        _,h = t.wrap(CW,1000)
        self.check(h+12)
        t.drawOn(self.c,M,self.y-h)
        self.y -= h+12

    def figure(self,eid,caption,crop,width=CW):
        item = next(x for x in self.evidence if x['id']==eid)
        original = ROOT/item['file']
        with Image.open(original) as src:
            im = src.crop(crop)
            height = width*im.height/im.width
            self.check(height+45)
            x=M+(CW-width)/2
            self.c.drawImage(ImageReader(im),x,self.y-height,width=width,height=height)
            self.c.setStrokeColor(LINE)
            self.c.rect(x,self.y-height,width,height,fill=0,stroke=1)
        self.y -= height+7
        num = len(self.figures)+1
        self.para(f'<b>Figure {num} — {caption}</b> · {eid}. Recadrage de la capture originale.','caption')
        self.figures.append(dict(number=num,evidence=eid,file=item['file'],page=self.page,crop=list(crop),caption=caption))

    def source(self,label):
        url = SOURCES[label]
        self.para(f'Source externe : <a href="{escape(url)}" color="#0078D4">{label}</a> · documentation consultée le 27/11/2026.','small')

    def code(self,lines):
        self.box('Extrait du fichier local — variante command component', '<font name="Mono" size="8">'+ '<br/>'.join(escape(x).replace(' ','&#160;') for x in lines)+'</font>')

    def architecture(self):
        """Draw only services and paths supported by reviewed screenshots."""
        self.check(208)
        c=self.c
        y=self.y-64
        widths=[150,150,150]
        xs=[M,M+179,M+358]
        labels=[('SOURCE STOCKÉE','consumption/source/','pjme hourly.csv'),('DATA FACTORY','adf-forecastbrief1','pl_ingest_consumption'),('ZONE RAW','stforecastbrief1','raw/2026/11/25/')]
        for x,w,(a,b,d) in zip(xs,widths,labels):
            c.setFillColor(PALE);c.setStrokeColor(LINE)
            c.roundRect(x,y,w,64,5,fill=1,stroke=1)
            for j,(txt,font,sz,col) in enumerate([(a,'NotoBold',8,BLUE),(b,'Noto',8.1,TEXT),(d,'Noto',7.7,TEXT)]):
                c.setFont(font,sz);c.setFillColor(col);c.drawCentredString(x+w/2,y+45-j*16,txt)
        c.setStrokeColor(BLUE);c.setFillColor(BLUE)
        for x in [M+153,M+332]:
            c.line(x,y+32,x+22,y+32)
            p=c.beginPath();p.moveTo(x+22,y+32);p.lineTo(x+17,y+35);p.lineTo(x+17,y+29);p.close();c.drawPath(p,fill=1,stroke=0)
        y2=y-100
        c.line(M+433,y,M+433,y2+74)
        c.setFillColor(NAVY);c.roundRect(M,y2,CW,74,5,fill=1,stroke=0)
        c.setFillColor(white);c.setFont('NotoBold',10)
        c.drawString(M+13,y2+52,'AZURE MACHINE LEARNING · ml-forecastbrief1 · cpu-forecast')
        c.setFont('Noto',9)
        c.drawString(M+13,y2+31,'Préparation / séparation / Decision Forest / Score / Evaluate')
        c.drawString(M+13,y2+13,'Datastore ADLS enregistré ; continuité exacte vers les assets Classic à tracer')
        self.y=y2-12
        self.para('Schéma de synthèse — E07, E15–E20, E29–E38, E50–E54. La liaison vers ML représente le chemin prévu ; les preuves ne couvrent pas tous les changements d’assets. Le job d’inférence ultérieur est dans ml-forecastbrief-1-2 (E61–E64).','caption')

    def finish(self):
        assert self.page == 15
        self.c.save()
        (OUT/'figure_manifest.json').write_text(json.dumps(self.figures,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(f'Created {self.page} pages, {len(self.figures)} figures / {len(set(x["evidence"] for x in self.figures))} distinct screenshots')


def main():
    r=Report()

    # 01 — Cover
    r.new('', '')
    r.y=H-116
    r.para('RAPPORT FINAL · PROJET TECHNIQUE','small',size=10)
    r.y-=24
    r.para('Conception et mise en œuvre<br/>d’un pipeline End-to-End',size=29,leading=37)
    r.para('de Data Engineering et de Machine Learning sur Microsoft Azure pour la prévision de la consommation électrique',size=20,leading=28)
    r.y-=24
    r.c.setStrokeColor(BLUE);r.c.setLineWidth(3);r.c.line(M,r.y,M+82,r.y)
    r.y-=30
    r.para('Microsoft Azure / Data Engineering / Machine Learning','h2')
    r.para('Auteur : <b>Houssam MIRROU</b><br/>Cadre : formation Simplon — intitulé exact du parcours non fourni<br/>Date de remise : <b>27 novembre 2026</b>')
    r.y-=20
    r.box('Du CSV à l’évaluation d’un modèle de régression',
          'Ingestion ADF démontrée · Stockage hiérarchique · Designer Classic · Modèle enregistré · Job d’inférence terminé')
    r.para('Périmètre documentaire : 64 captures inspectées visuellement, trois scripts Python et trois définitions YAML. Les résultats, les limites de preuve et les travaux restant à finaliser sont distingués dans le rapport.','small')
    r.y-=12
    r.para('Période indiquée dans le brief : du 23/11/2025 au 27/11/2026 à 17:30. L’écart d’année apparent est conservé et discuté en introduction.','small')

    # 02 — Executive summary and contents
    r.new('02 / Résumé exécutif', 'Une chaîne Azure démontrée,<br/>une mise en production à compléter')
    r.para('L’objectif est de construire, dans un contexte fintech, une chaîne de préparation et de modélisation de la consommation électrique horaire. Azure Data Factory copie les données vers un stockage Azure à espace de noms hiérarchique ; Azure Machine Learning assure l’exploration, le prétraitement, l’apprentissage et l’évaluation.')
    r.para('Les captures confirment une copie ADF réussie, une forêt de régression dans Designer Classic, des prédictions sur <b>29 074 observations</b> et l’enregistrement de <b>forecastingmodelv1, version 1</b>. Un job d’inférence est ensuite <b>Completed</b> dans un autre workspace. La disponibilité d’une API temps réel n’est pas démontrée. [E29, E53–E55, E61–E64]')
    r.box('Résultat vérifié : performance explicative modérée',
          'MAE : <b>3 177,774545 MW</b> · RMSE : <b>4 251,194918 MW</b><br/>R² : <b>0,570777</b>. Ces valeurs appartiennent au run Classic du 25/11 ; elles ne sont pas attribuées au job d’inférence du 26/11.')
    r.sub('Sommaire')
    r.table(['Section','Page'],[
        ('03 · Introduction et contexte métier / 04 · Architecture','3'),
        ('05 · Ingestion et orchestration','4'),
        ('06 · Stockage et organisation','5'),
        ('Infrastructure ML : workspace et calcul CPU','6'),
        ('07 · Analyse exploratoire','7'),
        ('08 · Prétraitement et Feature Engineering','8'),
        ('09 · Préparation et séparation temporelle','9'),
        ('10 · Entraînement du modèle','10'),
        ('11 · Évaluation des performances','11'),
        ('12 · Enregistrement et inférence','12'),
        ('13 · Gouvernance, sécurité et RGPD','13'),
        ('14 · Difficultés / 15 · Conclusion et perspectives','14'),
        ('16 · Annexes : code, preuves et références','15'),
    ],[CW-45,45])

    # 03 — Context and architecture
    r.new('03 / Introduction et contexte métier', 'Prévoir la consommation,<br/>structurer un flux traçable')
    r.para('Le rôle de Data Developer en fintech conduit ici à traiter une série énergétique comme cas d’usage de pipeline de données et de Machine Learning. Une prévision peut contribuer à une analyse de risque ou à une simulation d’exposition énergétique ; aucun bénéfice financier ni usage métier en production n’a été mesuré dans ce projet.')
    r.para('La cible <b>PJME_MW</b> représente une puissance électrique agrégée, exprimée en mégawatts. Malgré le terme « consommation » du sujet, il ne s’agit pas directement d’une énergie en MWh. <b>Datetime</b> situe l’observation horaire. Le modèle démontré apprend essentiellement les régularités calendaires de cette série.')
    r.sub('04 / Architecture technique')
    r.architecture()
    r.para('ADF réalise la copie depuis un fichier déjà déposé dans Azure Storage. Le traitement tabulaire et l’apprentissage sont portés par le calcul CPU d’Azure ML. Aucune VM de traitement autonome, activité ADF déclenchant ML ou orchestration intégrale planifiée n’est démontrée : la chaîne est documentée par étapes successives.')
    r.box('Contraintes du cahier des charges',
          'North Europe ; CPU avec autoscaling de 0 à 1 nœud ; séparation temporelle 80/20 ; qualité, sécurité et reproductibilité. Le brief indique 23/11/2025–27/11/2026 à 17:30, alors que les captures documentent les 24–26/11/2026 : l’année de début reste à clarifier.')

    # 04 — Ingestion
    r.new('05 / Ingestion et orchestration', 'Une copie ADF exécutée<br/>et vérifiée dans le stockage')
    r.para('La fabrique <b>adf-forecastbrief1</b> (V2, North Europe) utilise le service lié <b>ls_adls_forecast</b> de type ADLS Gen2. Le test de connexion est positif avec une clé de compte et <b>AutoResolveIntegrationRuntime</b>. Le dataset <b>ds_source_csv</b> référence <b>consumption/source/pjme hourly.csv</b>. [E10–E20]')
    r.para('La lecture est configurée en DelimitedText, séparateur virgule, UTF-8, sans compression, avec première ligne d’en-tête. L’aperçu montre Datetime et PJME_MW ; le mapping explicite conserve les deux colonnes, initialement déclarées String. Cela confirme un schéma lu, sans prouver une validation exhaustive de toutes les lignes. [E19, E20, E26]')
    r.figure('E29','Exécution réussie de pl_ingest_consumption', (830,965,2080,1370))
    r.para('L’activité <b>copy_consumption_csv</b> et le pipeline portent le statut <b>Succeeded</b>. Le démarrage affiché est le 25/11/2026 à 09:59:26, pour une activité de <b>17 s</b>. Le run est identifié par <b>8748d7a7-51ac-43ad-81fe-6085a3b4ea2f</b>. La présence du CSV en destination est confirmée séparément dans le stockage. [E29, E30]')
    r.sub('Portée de l’orchestration')
    r.para('Le pipeline contient une activité de copie. Les captures ne montrent ni déclencheur récurrent ni dépendance d’exécution vers Azure ML. Pour automatiser l’ensemble, il resterait à paramétrer la date d’ingestion, les contrôles bloquants, les reprises et le lancement du job ML après validation du dépôt.')
    r.para('Le premier essai produit une extension .txt, cohérente avec le paramètre de sink visible ; une seconde exécution produit le .csv. Les deux fichiers restent visibles. Les durées et statuts de ces essais sont conservés séparément. [E24, E27–E30]','small')

    # 05 — Storage
    r.new('06 / Stockage et organisation des données', 'Une zone raw datée,<br/>une filiation à consolider')
    r.para('Le compte <b>stforecastbrief1</b> est provisionné dans <b>HMirrou</b>, en North Europe : StorageV2, performance Standard, réplication LRS, niveau Hot et espace de noms hiérarchique activé. Le conteneur <b>consumption</b> est privé. Les chemins observés distinguent <b>source/</b> et <b>raw/YYYY/MM/DD/</b>. [E07–E09, E17, E30]')
    r.figure('E30','Fichiers présents dans raw/2026/11/25/',(420,397,2240,805))
    r.para('Le fichier source est affiché à <b>3,88 MiB</b> ; les sorties .txt et .csv sont à <b>4,57 MiB</b>. Une copie DelimitedText peut réécrire l’encodage textuel et les guillemets : le dossier « raw » est ici une zone d’atterrissage logique. L’identité binaire avec le fichier original n’est pas établie ; il faudrait comparer les empreintes des fichiers. [E17, E20, E24, E28, E30]')
    r.sub('ADLS Gen2 et accès aux données depuis Azure ML')
    r.para('Dans le workspace initial, <b>ds_adls_forecast</b> est enregistré comme datastore <b>Azure Data Lake Storage Gen2</b>. L’asset <b>pjme_consumption:1</b>, de type uri_file, pointe vers <b>raw/2026/11/25/pjme hourly.csv</b> via une URI <b>dfs.core.windows.net</b>. L’enregistrement d’un datastore ou d’un asset ne garantit pas, à lui seul, une lecture réussie par un job. [E33–E38]')
    r.box('Limite documentaire : la connexion finale',
          'Les notes de projet signalent un repli réussi vers Blob Storage après des erreurs ADLS. Aucune capture ne montre ce repli ni son datastore. Le rapport confirme donc le datastore ADLS enregistré et les sorties ML visibles, sans certifier le connecteur final des assets Classic.')
    r.para('Pour la traçabilité, associer chaque dépôt à son chemin complet, sa date, son empreinte, son schéma et son run ADF. Les assets Classic pjme_consumption2 et pjme_consumption_3 sont visibles, mais leur filiation exacte avec pjme_consumption:1 n’est pas exportée.','small')

    # 06 — Compute
    r.new('Infrastructure Azure Machine Learning', 'Un cluster CPU adapté<br/>à l’exercice et au coût à l’usage')
    r.para('Le workspace <b>ml-forecastbrief1</b> présente un état de provisionnement <b>Succeeded</b> en North Europe. Ses ressources associées comprennent un stockage de workspace, un Key Vault et Application Insights. Leur présence n’atteste pas une gestion des secrets ou une supervision applicative effectivement configurée. [E31, E32]')
    r.figure('E36','Configuration de cpu-forecast et de son autoscaling',(650,475,2525,1090))
    r.table(['Élément','Configuration observée'],[
        ('Cluster','cpu-forecast ; CPU ; Dedicated ; Linux'),
        ('Taille de VM','Standard_DS11_v2 ; 2 vCPU ; 14 GiB selon Microsoft'),
        ('Autoscaling','Minimum 0 ; maximum 1 ; réduction après 120 s d’inactivité'),
        ('État ultérieur','Allocation Succeeded (1 node), nœud en préparation à l’instant E47'),
    ],[125,CW-125])
    r.para('Les réglages 0–1 limitent la capacité et permettent une extinction du calcul inutilisé ; ils ne prouvent pas qu’un cycle complet de montée et de descente a été observé. Le calcul a été sélectionné dans la soumission du job EDA. [E36, E44, E47]')
    r.box('Rectification de la spécification matérielle',
          'Le brief associe « StandardDS2v3 » à 2 vCPU et 14 GB. Si l’intention est Standard_D2s_v3, la fiche officielle indique <b>2 vCPU et 8 GiB</b>. La taille réellement visible est <b>Standard_DS11_v2</b>, à <b>2 vCPU et 14 GiB</b>. Les deux références ne sont pas interchangeables.')
    r.source('DSv3');r.source('DSv2')

    # 07 — EDA
    r.new('07 / Analyse exploratoire des données', '145 366 observations,<br/>des horodatages répétés à examiner')
    r.para('La sortie <b>Summarize Data</b> fournit une ligne par variable et 23 statistiques. Le « Rows = 2 » de cette vue désigne les deux variables résumées ; il ne correspond pas à l’effectif du jeu initial. Les deux valeurs <b>Count = 145366</b> permettent d’établir le volume observé. [E48]')
    r.figure('E48','Statistiques descriptives réellement produites',(390,350,1745,910))
    r.table(['Indicateur','Valeur visible'],[
        ('Effectif / colonnes originales','145 366 / Datetime et PJME_MW'),
        ('Manquants déclarés','0 pour Datetime ; 0 pour PJME_MW'),
        ('Timestamps distincts','145 362'),
        ('PJME_MW : min / max','14 544,0 / 62 009,0 MW'),
        ('PJME_MW : moyenne / médiane','32 080,222830648156 / 31 421,0 MW'),
        ('Bornes Datetime affichées','Du 2002-01-01 01:00:00+00:00<br/>au 2018-08-03 00:00:00+00:00'),
    ],[190,CW-190])
    r.para('L’écart entre effectif et timestamps distincts indique <b>quatre occurrences au-delà de l’unicité</b>. Cela ne prouve pas quatre lignes identiques : des heures répétées peuvent porter des mesures différentes. Leur cause, le fuseau d’origine et une éventuelle ambiguïté d’heure locale ne sont pas établis.')
    r.para('L’absence de manquants déclarés n’exclut ni des heures absentes de la série ni des valeurs atypiques. Un contrôle de continuité horaire et une analyse des pics restent à produire. Les bornes +00:00 sont celles affichées par l’outil ; elles ne certifient pas le fuseau de collecte.','small')

    # 08 — Preprocessing
    r.new('08 / Prétraitement et Feature Engineering', 'Nettoyer les types,<br/>extraire les régularités calendaires')
    r.para('Le graphe exécuté enchaîne <b>Clean Missing Data, Remove Duplicate Rows, deux Edit Metadata et Execute Python Script</b>. Les coches vertes, accompagnées pour certaines étapes d’icônes de réutilisation, attestent des sorties disponibles pour ces composants ; les paramètres détaillés de nettoyage et de conversion ne sont pas affichés. [E51]')
    r.figure('E51','Prétraitements terminés ou réutilisés dans le job Classic',(1520,565,2430,1365),width=298)
    r.para('Le nettoyage sert à sécuriser les entrées ; puisque l’EDA ne rapporte aucun manquant sur les deux colonnes, aucun volume de lignes supprimées ne peut lui être attribué. De même, la présence de Remove Duplicate Rows ne renseigne pas les colonnes retenues ni le nombre supprimé. Les étapes Edit Metadata préparent les types requis ; leur configuration exacte n’est pas fournie.')
    r.para('L’aperçu des prédictions confirme les six variables <b>Hour, DayOfWeek, Month, Quarter, Year, DayOfYear</b>. Elles décrivent l’heure, le jour de semaine, le mois, le trimestre, l’année et le rang du jour dans l’année. Ces attributs sont connus pour une date future et peuvent représenter des cycles d’activité sans utiliser la cible future. [E54]')
    r.para('Le script local prepare.py propose une implémentation proche mais distincte : il dédoublonne par timestamp et emploie les noms Dayofweek et Dayofyear. Il ne permet pas de reconstituer à l’identique le code Python embarqué du pipeline Classic.','small')

    # 09 — Temporal separation
    r.new('09 / Préparation et séparation temporelle', 'Tester sur le futur :<br/>une exigence centrale de validation')
    r.para('Pour une prévision, une coupe aléatoire peut mélanger des observations proches et faire apprendre au modèle des régimes provenant de la période à évaluer. Le protocole attendu trie les données par Datetime, réserve les <b>80 % les plus anciens</b> à l’apprentissage et les <b>20 % les plus récents</b> au test. Le réglage « 80/20 » seul ne garantit pas cette propriété.')
    r.table(['Niveau de preuve','Constat'],[
        ('Câblage visible','Split Data fournit deux sorties vers des sélections de colonnes, puis Train Model et Score Model. [E50, E52]'),
        ('Effectif observé','Le jeu scoré contient 29 074 lignes. Il est compatible avec environ 20 % de 145 366, sans prouver à lui seul la chronologie. [E48, E54]'),
        ('Notes de réalisation','Un indicateur train_flag est décrit pour piloter Split Data ; ni sa construction ni l’expression du composant ne sont visibles.'),
        ('Code local vérifiable','prepare.py trie par Datetime puis coupe avec iloc à int(len(df) * 0.8), après suppression des timestamps répétés.'),
        ('Preuve manquante','Bornes complètes train/test et assertion max(train.Datetime) &lt; min(test.Datetime) pour le run Classic.'),
    ],[123,CW-123])
    r.figure('E54','Effectif du test, variables calendaires et premières prédictions',(380,270,1355,610))
    r.para('Une implémentation par train_flag peut affecter chaque ligne à une période, puis utiliser une expression de Split Data pour router les lignes. Microsoft documente ce mode de séparation conditionnelle. Son application exacte au run fourni reste à prouver. La variable de routage et l’horodatage doivent être exclus des entrées du modèle après la coupe.')
    r.source('Split Data')
    r.para('Avant une validation finale, exporter l’audit de la coupe et vérifier que les transformations apprises sur les données, si elles existent, sont ajustées uniquement sur l’entraînement. Le code local fournit une stratégie, mais aucun audit.json exécuté n’est disponible.','small')

    # 10 — Training
    r.new('10 / Entraînement du modèle', 'Decision Forest Regression<br/>dans Azure ML Classic Designer')
    r.para('Le modèle effectivement visible est <b>Decision Forest Regression</b>. Il est connecté à <b>Train Model</b>, qui reçoit le jeu d’apprentissage après sélection des colonnes. Le modèle entraîné et le jeu de test convergent ensuite vers <b>Score Model</b> ; sa sortie alimente <b>Evaluate Model</b>. [E50–E54]')
    r.figure('E50','Connexion de la forêt de régression à Train Model',(360,780,1840,1250))
    r.para('Une forêt de régression combine plusieurs arbres pour approximer des relations non linéaires et leurs interactions. Ce choix convient à une première modélisation de la saisonnalité calendaire. Il ne représente pas explicitement la dynamique séquentielle : aucune valeur retardée de consommation ni statistique glissante n’est visible dans les variables de test.')
    r.table(['Rôle','Éléments établis'],[
        ('Cible','PJME_MW ; nature régression confirmée par les sorties scorées et les métriques.'),
        ('Variables explicatives','Hour, DayOfWeek, Month, Quarter, Year, DayOfYear visibles dans le jeu scoré. [E54]'),
        ('Sélection','Deux Select Columns in Dataset visibles après Split Data ; détail des sélecteurs non affiché.'),
        ('Hyperparamètres Classic','Nombre d’arbres, profondeur, graine et stratégie de recherche non visibles : valeurs non attribuées.'),
    ],[130,CW-130])
    r.box('Variante Python : un artefact de conception distinct',
          'Les fichiers locaux configurent RandomForestRegressor : 60 arbres, profondeur 16, feuille minimale 5, n_jobs=2, random_state=42. Les composants sont enregistrés et placés sur un autre canvas (E42), mais aucune exécution réussie n’est fournie. Ces paramètres ne décrivent pas la forêt Classic évaluée.')
    r.para('La disponibilité de résultats d’évaluation atteste que des prédictions ont été produites ; les captures intermédiaires E51–E52 montrent encore le job Running. Elles ne sont donc pas utilisées pour annoncer un statut Completed de l’ensemble du job d’entraînement.','small')

    # 11 — Evaluation
    r.new('11 / Évaluation des performances', 'Une performance modérée,<br/>des erreurs à analyser par période')
    r.figure('E53','Métriques du run Classic du 25 novembre',(380,270,1720,590))
    r.table(['Mesure','Valeur exacte visible','Lecture'],[
        ('MAE','3 177,774545 MW','Amplitude moyenne de l’erreur absolue.'),
        ('RMSE','4 251,194918 MW','Pénalise davantage les erreurs fortes.'),
        ('R²','0,570777','Environ 57,08 % de la variance expliquée sur ce test.'),
        ('Erreur relative quadratique','0,429223','Complément de R² dans cette sortie.'),
        ('Erreur relative absolue','0,630538','Valeur de l’évaluateur ; définition de référence à conserver.'),
        ('Observations test','29 074','Nombre de lignes du Scored_dataset. [E54]'),
    ],[119,126,CW-245])
    r.para('Le RMSE supérieur au MAE suggère des erreurs de grande amplitude pour certaines observations ; la distribution des résidus n’est pas disponible pour les caractériser. <b>R² = 0,570777 indique une performance explicative modérée</b>, sans démontrer une précision suffisante pour une décision opérationnelle. Ce score n’est ni un pourcentage de prédictions exactes ni une mesure d’incertitude.')
    r.para('Les valeurs du brief sont cohérentes avec cette capture après arrondi : RMSE 4 251,19 et R² 0,5708 ; le MAE arrondi à deux décimales serait <b>3 177,77</b>. La table conserve ici les six décimales effectivement affichées. Les métriques viennent du run <b>f9afd8ab-33a6-48ac-bbb0-432bac286e56</b>, également visible dans la table de prédictions. [E53, E54]')
    r.sub('Limites et améliorations proposées')
    r.para('Comparer à une prévision naïve J−1 et J−7 ; ajouter des retards et moyennes glissantes calculés uniquement à partir du passé disponible à l’horizon visé ; intégrer météo et jours fériés ; optimiser les hyperparamètres avec une validation temporelle glissante. Analyser les résidus par heure, saison et niveau de charge, puis évaluer plusieurs horizons de prévision.')
    r.para('Aucun résultat de baseline, intervalle de confiance, graphique de résidus ou métrique du job d’inférence ultérieur n’a été fourni. Ces éléments restent des travaux proposés.','small')

    # 12 — Registration and inference
    r.new('12 / Enregistrement et pipeline d’inférence', 'Modèle enregistré ;<br/>inférence exécutée comme job')
    r.figure('E55','forecastingmodelv1 enregistré en version 1',(400,470,1910,625))
    r.para('La liste Models confirme <b>forecastingmodelv1:1</b>, type CUSTOM, dans l’expérience <b>train_model_experiment</b>, créé le 25/11/2026 à 17:15. Le run source affiché est un identifiant enfant tronqué ; la liaison exacte entre cet artefact enregistré et toutes les métriques doit être conservée dans un export de métadonnées. [E55]')
    r.figure('E64','Job d’inférence Completed et Score Model réussi',(360,310,1800,1100))
    r.para('Les brouillons du 25/11 réutilisent une transformation et un modèle entraîné, puis Score Model et Web Service Output. Le 26/11, le run <b>67d0f4cf-1186-47d3-a67a-c1cd61a30b8c</b> est <b>Completed</b> dans <b>ml-forecastbrief-1-2 / experiment_2</b> ; les étapes Score Model et Evaluate Model sont vertes. Les captures de 11:38 et 13:36 correspondent au même run. [E56–E64]')
    r.box('Frontière entre job et service temps réel',
          'Création du graphe : vérifiée. Exécution du job d’inférence : vérifiée dans le second workspace. Qualité chiffrée de cette exécution : non fournie. Endpoint déployé, URL, authentification et appel API avec réponse : non démontrés. Aucun Web Service Input n’est visible sur les vues fournies.')

    # 13 — Governance
    r.new('13 / Gouvernance, sécurité et RGPD', 'Des contrôles observés,<br/>une conformité à documenter')
    r.para('La sécurité se juge à partir des paramètres effectivement visibles et de leur périmètre. Les captures démontrent plusieurs contrôles de stockage, mais elles ne constituent pas un audit complet des accès, du chiffrement, du réseau ou de la conformité juridique.')
    r.table(['Domaine','Démontré','À compléter / recommandé'],[
        ('Accès','Rôle utilisateur sur HMirrou ; conteneur Private ; accès anonyme aux blobs désactivé. [E02, E07, E08]','Revoir les droits effectifs et appliquer le moindre privilège ; documenter les identités de service.'),
        ('Authentification','ADF configuré avec Account key ; accès par clés autorisé sur le compte. [E07, E16]','Privilégier une identité managée lorsque possible ; protéger et renouveler les secrets.'),
        ('Transport / réseau','Secure transfer activé ; TLS min 1.2 ; accès réseau public tous réseaux ; aucun private endpoint. [E07]','Étudier filtrage réseau et accès privés selon le besoin. Privé au niveau du conteneur ne signifie pas réseau privé.'),
        ('Protection des données','Soft delete blobs/conteneurs 7 jours ; versioning désactivé. [E07]','Définir conservation et restauration ; vérifier un test de reprise. Aucun test fourni.'),
        ('Qualité / filiation','Statistiques E48 ; étapes de nettoyage ; runs et version modèle visibles.','Exporter volumes, schémas, bornes temporelles, paramètres et relations entre assets.'),
        ('Reproductibilité','Scripts/YAML disponibles ; modèle versionné dans l’interface.','Figer dépendances et image environnement ; exporter le pipeline Classic et ses scripts embarqués.'),
    ],[88,190,CW-278])
    r.sub('RGPD : portée et mesures proposées')
    r.para('Les colonnes visibles décrivent une mesure énergétique agrégée et un horodatage ; aucune identité individuelle n’y apparaît. Cela ne suffit pas à certifier l’anonymat de toutes les données ou de leurs usages. Si des données personnelles sont introduites, documenter finalité, minimisation, conservation, information des personnes et mesures de sécurité conformément aux principes rappelés par la CNIL.')
    r.source('CNIL')
    r.para('L’hébergement en North Europe ne suffit pas à établir une conformité RGPD complète. Aucun registre de traitement, analyse des destinataires, politique de conservation ou examen des transferts n’est fourni. Les captures contiennent par ailleurs un nom et des identifiants de compte : leur diffusion doit être limitée au contexte d’évaluation.','small')

    # 14 — Challenges and conclusion
    r.new('14 / Difficultés rencontrées et solutions', 'Documenter les écarts,<br/>prioriser la validation restante')
    r.table(['Incident / constat documenté','Résolution ou limite de preuve'],[
        ('Destination initiale en .txt','Le sink affiche .txt ; une première sortie texte est visible. Un second run réussi produit aussi le .csv dans raw/2026/11/25. Le changement exact de réglage n’est pas capturé. [E24, E28–E30]'),
        ('Aperçu destination en échec','Un message Failed partiel reste visible alors que la publication est réussie. La cause ne peut pas être lue. Le succès de copie ultérieur prouve la réussite de cette étape. [E21, E22, E29]'),
        ('Asset absent du Designer puis visible','No data assets found précède l’apparition et le placement de pjme_consumption. Aucun diagnostic causal n’est fourni. [E39–E41]'),
        ('Changement de workspace','ml-forecastbrief1 est remplacé dans les captures d’inférence par ml-forecastbrief-1-2. Le motif de ce changement et la reprise des configurations ne sont pas démontrés. [E32, E61]'),
    ],[161,CW-161])
    r.para('Les erreurs d’authentification ADLS, le repli Blob, le conflit soft-deleted workspace et les erreurs d’expression Split Data sont mentionnés dans les notes, mais sans capture ni journal correspondant. Ils ne sont donc pas présentés comme des incidents vérifiés ni comme des causes prouvées des changements de ressources.')
    r.sub('15 / Conclusion et perspectives')
    r.para('Le projet établit une base fonctionnelle de Data Engineering et de Machine Learning sur Azure : ingestion réussie, organisation du stockage, exploration des données, chaîne Classic de régression, évaluation disponible, enregistrement de modèle et exécution d’un job d’inférence. Le résultat évalué reste modéré, avec une erreur absolue moyenne de <b>3 177,774545 MW</b>.')
    r.para('La robustesse de la prévision et l’exploitabilité du système exigent encore un audit de la coupe temporelle du run Classic, une filiation complète entre les assets et les workspaces, ainsi qu’une validation du contrat d’inférence. Le modèle peut être amélioré par des variables historiques et externes, puis comparé à des références temporelles simples.')
    r.box('Priorités de finalisation',
          '<b>1.</b> Exporter le pipeline, le code embarqué et l’audit train/test.<br/>'
          '<b>2.</b> Identifier le datastore réellement utilisé par chaque asset.<br/>'
          '<b>3.</b> Valider les baselines et l’inférence sur des entrées futures sans cible.<br/>'
          '<b>4.</b> Déployer et tester un endpoint, puis automatiser et superviser le flux.')

    # 15 — Annexes
    r.new('16 / Annexes', 'Sources techniques<br/>et dossier de reproductibilité')
    r.sub('A · Extrait du Feature Engineering local')
    r.para('Extrait exact de Script/01_prepare/src/prepare.py. Il documente la variante Python disponible ; le code embarqué du Designer Classic n’est pas fourni et ses noms de colonnes diffèrent par la casse.','small')
    r.code([
        'dt = df["Datetime"].dt',
        'df["Hour"] = dt.hour',
        'df["Dayofweek"] = dt.dayofweek',
        'df["Month"] = dt.month',
        'df["Quarter"] = dt.quarter',
        'df["Year"] = dt.year',
        'df["Dayofyear"] = dt.dayofyear',
    ])
    r.sub('B · Composants et artefacts locaux')
    r.table(['Fichier / artefact','Portée'],[
        ('Script/01_prepare/prepare.yml<br/>Script/01_prepare/src/prepare.py','Entrée uri_file ; sorties train/test/audit ; contrôle des colonnes, parsing, tri et dédoublonnage des timestamps.'),
        ('Script/02_train/train.yml<br/>Script/02_train/src/train.py','RandomForestRegressor ; sortie prévue model.joblib et training_info.json ; exécution non démontrée.'),
        ('Script/03_evaluate/evaluate.yml<br/>Script/03_evaluate/src/evaluate.py','Exports prévus metrics.json et predictions.csv ; comparaison à la moyenne d’entraînement ; résultats absents.'),
        ('pjme_azure_components.zip','Six fichiers identiques à Script/ ; README explicite de non-exécution. Les YAML référencent sklearn-1.5/labels/latest : version d’environnement à figer.'),
    ],[230,CW-230])
    r.sub('C · Références et correspondance des preuves')
    r.para('Les identifiants E01–E64 renvoient aux noms complets dans <b>report/evidence_inventory.md</b>. Les empreintes des originaux figurent dans <b>evidence_manifest.json</b> ; les recadrages et pages des figures dans <b>figure_manifest.json</b>. Le générateur <b>generate_report.py</b> produit ce PDF sans contacter Azure. Aucun CSV source ni résultat exporté n’est présent dans le dossier initial.','small')
    for label,title in [('DSv3','Microsoft Learn — caractéristiques Dsv3'),('DSv2','Microsoft Learn — caractéristiques DSv2 à mémoire optimisée'),('Split Data','Microsoft Learn — composant Split Data'),('CNIL','CNIL — six grands principes du RGPD')]:
        r.para(f'<a href="{escape(SOURCES[label])}" color="#0078D4">{title}</a> · consulté le 27/11/2026.','small')
    r.para('Le texte du cahier des charges est celui joint à la demande ; aucun autre énoncé indépendant n’a été trouvé. Les nombres de ce rapport sont transcrits des captures, sans nouvel entraînement ni recalcul des métriques.','small')
    r.finish()


if __name__ == '__main__':
    main()
