# scrapping_vdm
Petit programme de scrapping du site vdm


########## Notes générales ###############

Gestion des bibliothèques :
pip install -r requirements.txt 


S'utilise en lançant "python app.py" via la console.
L'accès au site web local est affiché dans la console.

Les URIs sont :
127.0.0.1/api/posts -> affiche les 200 derniers posts
127.0.0.1/api/posts/<ID> -> récupère le post d'ID donné, si il existe
127.0.0.1/api/posts/author=<auteur> -> récupère tous les postes d'un autre donné
127.0.0.1/api/posts/from=<2017-09-28T09:00:00Z>&to=<2017-12-31T00:00:00Z> -> récupère tous les postes entre ces deux dates, dates à mettre a ce format la spécifiquement. 

#############################################
Courte description des fichiers :

app.py -> contient l'api flask qui gère l'affichage des informations
extractor.py -> contient le scrappeur qui va chercher l'information sur le site VDM
form.py -> contient le code qui demande la ligne de commande ("fetch")
testing.py -> contient les test unitaires des fonctions principales. Pour les lancer, il faut utiliser la commande "python testing.py"

##############################################
