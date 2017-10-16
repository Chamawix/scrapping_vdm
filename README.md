# scrapping_vdm
Petit programme de scrapping du site vdm


########## Notes générales ###############

Installation des bibliothèques :
pip install -r requirements.txt 


####
Notice d'utilisation du scrapper:
####
En lançant "python app.py" via la console.


Les URLs sont :
127.0.0.1/api/posts -> affiche les 200 derniers posts
127.0.0.1/api/posts/<ID> -> récupère le post d'ID donné, si il existe
127.0.0.1/api/posts/author=<auteur> -> récupère tous les postes d'un auteur donné
127.0.0.1/api/posts/from=<2017-09-28T09:00:00Z>&to=<2017-12-31T00:00:00Z> -> récupère tous les postes entre ces deux dates, dates à mettre a ce format la spécifiquement. 


####
Notice d'utilisation du classifieur :
####
En lançant "python classification.py" via la console. 
Il est impossible, du fait de l'utilisation de Treetagger (qui n'est pas une bibliothèque python), de process directement du texte à partir de l'application. 
Pour le moment, on peut utiliser le texte en exemple. 
Les données issues du preprocessing se trouvent dans testing_data.csv

#############################################
Courte description des fichiers :
#############################################

app.py -> contient l'api flask qui gère l'affichage des informations
extractor.py -> contient le scrappeur qui va chercher l'information sur le site VDM
form.py -> contient le code qui demande la ligne de commande ("fetch")
testing.py -> contient les test unitaires des fonctions principales. Pour les lancer, il faut utiliser la commande "python testing.py"
classification.py-> contient la classe de classification, on entraine en runtime le classifieur via des données pre-traitées. 

#############################################
Dockerisation : 
#############################################

Fonctionne pour le master, pas pour les branches en cours de developpement. 

#############################################
License :
#############################################

Le programme nécessite l'installation et l'utilisation de Treetagger, qui permet de faire du TALN en français. 
Le code de ce programme est open-source, mais l'utilisation de Treetagger empêche une utilisation commerciale. 
Le projet utilise et modifie légèrement le code de python-treetagger de :  Copyright (C) Mirko Otto, auteur cité dans treetagger_python2.py. 

Remerciements pour l'utilisation de FEEL.csv :
Amine Abdaoui, Jérôme Azé, Sandra Bringay et Pascal Poncelet. FEEL: French Expanded Emotion Lexicon. Language Resources and Evaluation, LRE 2016, pp 1-23.
Remierciements pour l'utilisation de preprocessor :
Said özcan