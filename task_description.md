# COVID-XRAY- Klassifikation und Erklärungswerkzeug

## Motivation
Zur Erkennung einer Infektion mit COVID-19 existiert ein sehr guter und günstiger PCR-Test. Trotzdem stellt es selbst hochentwickelte Länder vor große Herausforderungen überall Tests verfügbar zu machen. Um bei nicht-verfügbaren Tests weiterhin COVID-19 von anders verursachten Lungenentzündungen unterscheiden zu könnnen, werden alternative Klassifikationsmethoden z.B. auf Basis von Röntgen- oder CT-Aufnahmen benötigt.
Die aktuelle Coronaviruskrise zwingt Arzte die Anwendung von KI-Methoden zur Erkennung und Beurteilung von Bilddaten in Betracht zu ziehen.  Verschiedene Gruppen und Unternehmen beschäftigen sich bereits mit KI-Methoden zur Klassifikation von COVID-19. Dazu werden Bilddaten aus verschiedenen Veröffentlichungen zusammengetragen und Auswertungsmethoden entwickelt.

## Zielstellung
Die Menge der verfügbaren Daten reicht bisher nicht aus um ein valides in der Medizin anwendbares diagnostisches Werkzeug zu entwickeln. Ziel des Praktikums ist es vielmehr den Arbeitsprozess eines DataScientists anhand des gegebenen Beispiels nachzuvollziehen.
Im Praktikum soll von der Datenauswahl/Transformation über Modellbildung und Applikationsentwicklung ein prototypisches System entwickelt werden welches zukünftig - wenn mehr Daten zur Verfügung stehen und Validierungstests durchgeführt wurden - als diagnostische Ergänzung per Web nutzbar wäre.

Auf Basis der gegebenen gelabelten Daten soll zunächst ein Klassifikationsmodell entwickelt werden. Existierende Beispiele erklären bisher nicht welche Regionen eines Röntgenbildes für die Klassifikation entscheidend waren. Dazu sollen 1-2 Verfahren (z.B. GradCAM oder eine  Alternative) angewendet werden um Heatmaps über gegebene klassifizierte Bilder zu erzeugen. Diese sollen erklären welche Bereiche den größten Einfluss auf eine Klassifikationsentscheidung hatten.

Das entwickelte Modell und die Heatmaps sollen dann in einer prototypischen Webanwendung dargestellt werden. Die Webanwendung soll es ermöglichen neue Bilder hochzuladen, zu klassifizieren und mittels Heatmap wichtige Regionen zu markieren.
Zusätzlich soll auch eine Erweiterung des Trainingsdatensatzes und Modellupdate möglich sein.
Die gesamte Anwendung wird als Docker-Anwendung entwickelt werden die ohne Installationsaufwand auf einer Maschine in der Universität Leipzig ausführbar ist.

## Arbeitspakete

### 1. Datenextraktion & Lösungsskizze
Im ersten Schritt sollen Daten eines frei verfügbaren Datensatzes geladen (https://github.com/ieee8023/covid-chestxray-dataset) und relevante Röntgenaufnahmen von COVID-19-Patienten zusammengetragen werden.
Zusätzlich soll aus Röntgenaufnahmen gesunder Patienten ein kleiner Datensatz extrahiert werden der bei der Klassifikation benötigt wird (
https://data.mendeley.com/datasets/rscbjbr9sj/2)
Der Datensatz enhält ebenfalls gelabelte Bilder mit anderen Krankheitsbildern die möglichst von COVID-19 unterschieden werden sollten.

Es ist eine Lösungsskizze zu erstellen welche alle Komponenten des Systems möglichst detailliert beschreibt. Dazu gehört die Datenextraktion/Transformation, Modellbildung, Erklärung mittels HeatMap sowie Webanwendung.

### 2. Modellbildung
- Basierend auf der Lösungsskizze sind die ML-Verfahren und die Anwendung zu implementieren. 
Die Lösungsskizze ist entsprechend zu aktualisieren.
Alle genutzten Quellen - auf für Codefragmente - sind zu nennen!

### 3. Evaluierung
- Das umgesetzte Verfahren ist hinsichtlich der Vorhersagequalität zu beurteilen. Hierzu eignen sich die Metriken Recall, Precision und F-Measure. Es ist zu untersuchen, inwieweit die Aufteilung von Trainings- und Testdaten, deren Umfang sowie verschiedene Parameter die Vorhersagequalität beeinflussen. Auch die Ergebnisse der berechneten Heatmaps sind auszuwerten.

### 4. Vortrag
- Ausarbeit einer 10-minütigen Präsentation, in welcher die Aufgabenstellung, die Lösungsskizze (kurze Beschreibung des Algorithmus/Architektur, Anwendung, sowie Nennung der verwendeten Bibliotheken) und die Ergebnisse der Evaluierung dargestellt werden. 

## Weiterführende Arbeiten

Da die Datengrundlage noch sehr dünn ist, könnte über GANs versucht werden einen Datengenerator zu entwickelt der COVID-19 Aufnahmen generiert die wiederum zum Training tieferer Netze nutzbar wären. 

## Darüber hinaus
Unter http://medicalsegmentation.com/covid19/ findet man auch ein sigemntiertes CT-Dataset welches genutzt werden könnte um ein automatisches Segmentieren von CT-Aufnahmen durchzuführen.
Da hier ebenfalls die Datenlage sehr dünn ist wäre eine Nutzung von GANs hier sicherlich interessant.

## Literatur

Existierendes Beispielwerkzeug  Werkzeug zur Klassifikation
https://mlmed.org/tools/xray/# 

Beispiel zu Klassifikation einer Lungenentzündung
https://www.kaggle.com/aakashnain/beating-everything-with-depthwise-convolution
