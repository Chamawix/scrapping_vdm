# -*- coding: utf-8 -*-
import nltk
from nltk import word_tokenize, wordpunct_tokenize
from nltk.stem import SnowballStemmer
import bs4
import pandas as pd
import codecs
from nltk.tag import pos_tag
import nltk.data
from nltk.corpus import stopwords
import re
from treetagger_python2 import TreeTagger
from extractor import strip_accents
import tweepy
from tweepy import OAuthHandler
import sys
import time
import numpy as np
import sklearn
import sklearn.cluster as cluster
import preprocessor as prepro
import matplotlib.pyplot as plt
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler 
from sklearn.naive_bayes import GaussianNB



french_stops = set(stopwords.words('french'))


encoding = "utf-8"


def deleteContent(pfile):
    pfile.seek(0)
    pfile.truncate()


dico = {
	# ARTICLES / DETERMINANTS
	"DET": ["le", "la", "les", "l'", "un", "une", "des", "d'",
		"du", "de", "au", "aux", "ce", "cet", "cette", "ces",
		"mon", "son", "ma", "ta", "sa", "mes", "ses",
		"notre", "votre", "leur", "nos", "vos", "leurs",
		"aucun", "aucune", "aucuns", 
		"tel", "telle", "tels", "telles",
		"tout", "toute", "tous", "toutes",
		"chaque"],
	# PRONOM
	"PRO": ["je", "tu", "il", "elle", "on", "nous", "vous", "ils", "elles",
		"me", "m'", "moi", "te", "t'", "toi",
		"se", "y", "le", "lui", "soi", "leur", "eux", "lui",
		"qui", "que", "quoi", "dont" "où"],
	# CONJONCTION
	"CONJ": ["mais", "ou", "et", "donc", "or", "ni", "car",
		"que", "quand", "qu", "qu'", "comme", "si",
		"lorsque", "quoique", "puisque"],
	# PREPOSITION
	"PREP": ["à", "derrière", "malgré", "sauf",
		"selon", "avant", "devant", "sous", "avec", 
		"en", "par", "sur", "entre", "parmi", 
		"envers", "pendant", "vers", "dans", "pour", "de", 
		"près", "depuis", "sans"]
}

syno=pd.read_table("Ressources/DictSyno.csv", dtype=None, delimiter ="@",header = 0, encoding = encoding)
asciisyno= [strip_accents(i) for i in syno.ix[:,0].values]
syno = syno.ix[:,:].values.tolist()

feel= pd.read_table("Ressources/FEEL.csv", dtype=None, delimiter =";",header = 0, encoding = encoding)
asciifeel= [strip_accents(i) for i in feel.ix[:,1].values]


class Classifier :

	#On passe la liste des articles extrait dans le init
	def __init__(self, infos = {"post":[], "class":[]}):

		self.training_set = None
		self.test_set = None
		self.tweets = infos
		self.clf=None
		self.scaler=StandardScaler()

	#Crée le classifieur, on utilise un classifieur bayésien naïf pour cet exercice, car on a accès à un certain nombre d'information classifiable rapidement.
	def create_classifier(self):
		training=pd.read_table("Data_apprentissage/actual_training.csv", dtype=None, delimiter ="@",header = 0, encoding = encoding)
		class_values = training.ix[:,0].values
		training_set = training.ix[:,1:].values
		print len(training_set[0])

		self.scaler.fit(training_set)
		#training_set = self.scaler.transform(training_set)
		#self.clf = MLPClassifier(solver='sgd', alpha=1e-5, hidden_layer_sizes=(3,15,5,2), random_state=1, warm_start=True, max_iter=1)
		self.clf = GaussianNB()
		self.clf = self.clf.fit(training_set, class_values)
		test_value=[[True,2,6,34,90,-0.675,0,3,2,1,0,1,0,0]]
		#print self.scaler.transform(test_value)
		#test_value=self.scaler.transform(test_value)
		print self.clf.predict((test_value))
		#self.testing_classifier()

	#Fonction de test pour évaluer rapidement l'efficacité du classifieur
	def testing_classifier(self):
		test_twitter= [u"Aujourd'hui par +30° j'ai eu le droit à un \"Mlle!Mlle! Je crois que ya une dame qui vous suis avec des collants pour vous\" #Joie #NTMFDChien",u"LE truc qu'il ne faut jamais faire putain... \"Tiens j'vais aller chez une coiffeuse que j'ai jamais vue de ma vie\". Erreur fatale bordel.",u"Mauvaise journee de merde, je vais au boulot, greve surprise de la RATP", u"Si vous passez une mauvaise journée, dites-vous que ma voiture est pleine d'impacts de marrons après m'être garé une nuit sous un marronnier",
		u"Aujourd'hui j'ai croise le plus grand footballeur africain de ma génération",u"Aujourd'hui, j'ai reussi à avancer dans ma vie, j'ai gagne en confiance!",u"Aujourd'hui j'ai pu revoir mes amis post bac pour la remise des diplomes. Je sais que je suis plus tout seul, et que c'est à moi de jouer",u"Ca veut dire 15 euros l\'kebab ? Meme pas en rêve",u"Aujourd’hui, j’ai décidé de quitter le Parti Socialiste. Je quitte un parti mais je ne quitte ni le socialisme ni les socialistes. #M1717"]
		self.preprocess(test_twitter)
		#test_val = pd.read_table("Data_apprentissage/testing_data.csv", dtype=None, delimiter ="@",header = 0, encoding = encoding) 
		
		reel_vdm = [0, 0, 0, 0, 1, 1, 1, 1, 1]
		#self.test_set = test_val

		#self.test_set = list(test_val.ix[:,:].values.tolist())
		#print self.test_set
		print self.test_set
		#self.test_set = self.scaler.transform(self.test_set)
		print self.clf.predict(self.test_set)

		pop = cluster.AgglomerativeClustering(n_clusters=2, linkage="ward").fit_predict(self.test_set)
		print pop
		print reel_vdm


	#fonction ayant déjà pré-process les donnees, qui utilise les information dans un fichier pre-fait. Pour le re-creer, necessite treetagger
	def get_bootstrap_testing_data(self, testing = True, preprocess=True):
		try :
			file =codecs.open("Data_apprentissage/tweets.txt", "r", "utf-8")
			
		except IOError:
			msg = "Unable to create file on disk."
		
		else :
			soup = bs4.BeautifulSoup(file, 'html.parser')
			prepro.set_options(prepro.OPT.URL, prepro.OPT.EMOJI)

			for txt in soup.find_all("tweet"):
				# Process a single status
				#print txt.text.encode(encoding)
				encod_text =txt.text.encode(encoding)
				txt = prepro.clean(encod_text)
				txt = strip_accents(txt)
				#print txt.encode(encoding)
				self.tweets["post"].append({"content":txt})

			file.close()

			
			if testing :
				#!!!! Ne fonctionne qu'avec treetagger !!!!!
				#self.preprocess(self.tweets, plain_text = False, has_tag=False, testing=testing)
				#Les données issues du preprocessing se trouvent dans testing_data.csv
				self.test_set = pd.read_table("Data_apprentissage/saved_testing_data.csv", dtype=None, delimiter ="@", encoding = encoding)
				
				self.create_classifier()
				cluster = self.clf.predict(self.test_set)
				print cluster
				for i in range(0,len(cluster)):
					if cluster[i] == 0:
						print ""
						print "###############"
						print ""
						print "Tweet detecte comme potentiellement interessant :"
						print ""
						print "###############"
						print ""
						print self.tweets["post"][i]["content"].encode(encoding)

			else :
				self.tweets = self.gather_all_vdm()
				self.preprocess(self.tweets, plain_text = False, has_tag=True, testing=testing)
				self.create_classifier()
				print self.clf.predict(self.test_set[1:])
			


	#Le coeur de la classe, il contient le preprocess des données d'entrainement & de cas réel. 
	def preprocess(self, text, plain_text = True , has_tag=False, testing=True):
		result_process= []

		try :
			if testing:
				gathering_data = open("Data_apprentissage/testing_data.csv", "w")
				
			else :
				gathering_data = open("Data_apprentissage/training_data.csv", "w")
				save_data = open("Data_apprentissage/saving.csv", "w")
				deleteContent(save_data)
			deleteContent(gathering_data)
		except IOError:
			msg = "Unable to create file on disk."
			return 0
		else:
			if not plain_text  :
				post = text["post"]
			else :
				post=text

			for tweets in post:
				#print tweets
				txt = tweets["content"]
				txt = txt.replace("'"," ")
				if has_tag :
					soup = bs4.BeautifulSoup(txt, "lxml")
					txt = soup.get_text()

				tokens = wordpunct_tokenize(txt)
				words = [w.lower() for w in tokens]
				words = [i for i in words if i not in [u'.', u'?', u'!', u',', u'\n',u'\n\n', u'VDM\n\n', u'VDM', u'VDM\n', u'?!',u"\"",u"#", u'!!']]
				vocab = sorted(set(words))

				nb_propositions = re.split("(?:"+"(?:"+" | ".join(str(x) for x in dico["CONJ"])+")"+"|"+"(?:"+"|".join(str(x) for x in ["\.", "\.\.", "\.\.\.", "\?","\!",":"])+"))",txt)

				for i in nb_propositions:
					if re.search("VDM(?! *\w+)", i) !=None or re.search("(?!\w)(?:"+" *| *".join(str(x) for x in dico["PREP"])+") (?!\w)", i.lower()) != None or  "" ==i:
						nb_propositions.remove(i)



				nb_phrase = re.split("(?:"+"|".join(str(x) for x in ["\.", "\.\.", "\.\.\.",":","\?\!","\?","\!"])+")", txt)
				for i in nb_phrase:
					#print len(i)
					#print i
					#print "VDM" in i
					if re.search("VDM(?! *\w+)", i) !=None:
						nb_phrase.remove(i)
					elif "VDM" in i or "#" in i:
						nb_phrase.remove(i)
					elif i=="" or i=="\n" or len(i)<3:
						nb_phrase.remove(i)
				tt = TreeTagger(language='french', encoding="utf-8")
				file=open("text_to_tag.txt", "w")
				file.write(txt.encode(encoding))
				file.close()

				result =tt.tag("C:\Users\Max\Desktop\scrapping_vdm\web\\text_to_tag.txt")
				
				if len(result[0])>1:
					try :
						all_possessif_per =  [i for i in result if i[1]== u'PRO:PER' or i[1] == u'DET:POS' or i[0].lower() in [u'm',u's',u'j',u't']]
						words_pos_tag =  [i[0] for i in result if i[1]!= u'PUN']
						words = [i for i in words_pos_tag if i in words]
					except :
						print "erreur sur le tagging"
						print result
						continue

					sentiments = self.calcul_polarity_score(result)
					has_chute = self.detect_chute(result, nb_phrase, txt)
					champs_lexical= self.detect_champs_lexical_vdm(result)
				else :
					print "erreur sur le tagging"
					print result
					continue

				#print all_possessif_per
				#print "ratio nb_mot / possessif/perso :" 
				if words != []:
					ratio_pro_mot= int((100*len(all_possessif_per))/len(words))
				else :
					ratio_pro_mot=0

				#print ratio_pro_mot
				#print "ratio de pronoms ciblant auteur des pronoms :"

				cible_perso = [i for i in  all_possessif_per if i[0].lower() in [u"j",u"je", u"nous", u"moi", u"ma", u"me", u"m", u'mon', u"notre"]]
				if all_possessif_per != []:
					ratio_cible_perso = (int((100*len(cible_perso))/len(all_possessif_per)))
				else :
					ratio_cible_perso=0
				if len(nb_propositions)>0 and len(vocab)>0:
					ratio_phrase_propositions = float(len(nb_phrase))/float(len(nb_propositions))
					ratio_propositions_vocab = float(len(nb_propositions))/float(len(vocab))
				else :
					ratio_phrase_propositions=0
					ratio_propositions_vocab=0

				intermed_result = [has_chute, ratio_phrase_propositions,ratio_propositions_vocab,ratio_pro_mot, ratio_cible_perso,sentiments["polarity"], sentiments["joy"],sentiments["fear"],sentiments["sadness"],sentiments["anger"],sentiments["surprise"],sentiments["disgust"], champs_lexical]
				if testing :
					result_process.append(intermed_result)
				else :
					#print text["post"][0]
					#print tweets
					#Si on train, on rajoute la class en pos 0 :
					result_process.append([self.tweets["class"][post.index(tweets)]]+intermed_result)
					s=""
					last_result = result_process[len(result_process)-1]

					for ir in last_result:
						s = s+str(ir)+"@"
					s = s+"\n"
					save_data.write(s)
				print "Avancement :"
				print 100*post.index(tweets)/len(post)


			#On rajoute les data de training pour le clustering 
			if testing :
				training=pd.read_table("Data_apprentissage/actual_training.csv", dtype=None, delimiter ="@",header = 0, encoding = encoding)
				include_training = training.ix[:,1:14].values
				save_process= result_process[:]
				#print len(result_process)
		
				for it in include_training:
					#print len(it)
					#print len(result_process[0])
					result_process.append(it.tolist())

			else :
				save_process = result_process

			print len(result_process[0])
			print len(result_process[len(result_process)-1])
			pop = cluster.AgglomerativeClustering(n_clusters=2, linkage="ward").fit_predict(result_process)
			s = ""

			#print save_process

			for i in save_process:
				i.append(pop[result_process.index(i)])
				s = s+str(i[0])
				for j in i[1:]:
					s = s+"@"+str(j)
				s = s+"\n"
				print s
				#time.sleep(0.1)
			gathering_data.write(s)
			
			if not testing :
				save_data.close()
			gathering_data.close()

			self.test_set=save_process



	

	#fonction assez simple qui définit une variable liée au champ lexical
	def detect_champs_lexical_vdm(self, tagged_text):
		#On va tester si on trouve des synonymes de divers champs lexicaux souvent présent dans les VDM :
		champs = ["jeu", "jouer", "geek", "informatique", "PC", "enfant", "garçon", "fille", "animal","transport","bus","métro", "voiture", "grève","voyager", "santé", "sexe","sexuel", "préliminaire", "amour","amoureux", "travail","travailler"]

		champs_ascii = ["jeu", "jouer", "geek", "informatique", "pc", "enfant", "garcon", "fille", "animal","transport","bus","metro", "voiture", "greve","voyager", "santé", "sexe","sexuel", "preliminaire", "amour","amoureux", "travail","travailler"]
		
		result = 0.0
		length_word = 1.0
		sentiment_gather = []
		for mono_tag in tagged_text:
			inflex = mono_tag[2].replace("\r","")
			#print inflex
			result = result+len([m for m in champs_ascii if m == inflex])
			#Peut on trouver des synonymes proche de nos mot-clefs?
			if inflex in asciisyno:
				length_word = length_word+1
				indexes = [i for i,x in enumerate(asciisyno) if x == inflex]
				#print indexes
				for index in indexes :
					result = result+ len([m for m in champs if m == syno[index][1]])

		if length_word>1:
			length_word = length_word-1
		
		result = float(result)/float(length_word)
		print result
		return result


	# Une VDM contient généralement une chute. 
	# Une VDM contient généralement au moins un pronom/determinant ciblant une possession de l'auteur, incluant l'auteur. Plus elle en contient, plus la cible est l'auteur
	# Si une VDM ne contient pas de cible, 
	def detect_chute(self,result_tag,phrases, clean_text):
		# Soit 1) une phrase très courte
		# Soit 2) une ponctuation favorable amenant la chute
		# soit 3) une phrase chargé de négatif

		#Une phrase unique, difficle de détecter la chute, on passe. 
		if len(phrases)<=1:
			return -1

		else :
			derniere_phrase = wordpunct_tokenize((phrases[len(phrases)-1]))
			#Très court, et sachant qu'on a éliminé les phrases "indesirables", on considère que c'est une chute 
			if len(derniere_phrase) <5:
				return 1
			#Dans une limite raisonnable de longueur, regardons si il y a ponctuation favorable amenant une chute:
			elif len(derniere_phrase) <20:
				try :
					curseur_poss = [m.start() for m in re.finditer(derniere_phrase[0], clean_text)]
				except :
					print "error in regex, return false"
					return -1
				#print curseur_poss
				possible_occurence_dans_phrase = len([i for i in derniere_phrase if i == derniere_phrase[0]])-1
				#print possible_occurence_dans_phrase
				curseur = curseur_poss[len(curseur_poss)-1 - possible_occurence_dans_phrase]

				for j in xrange(2,30,2):
					#print clean_text[curseur-j:curseur-j+2]
					if curseur - j >=0:
						if ".." in clean_text[curseur-j:curseur-j+2] or "!" in clean_text[curseur-j:curseur-j+2] or "?" in clean_text[curseur-j:curseur-j+2] or ":" in clean_text[curseur-j:curseur-j+2] or ";" in clean_text[curseur-j:curseur-j+2]:
							return 1

			#Test de négativité de la phrase :
			#print result_tag
			#print derniere_phrase[0]
			tag_dernier=None
			for i in result_tag:
				if derniere_phrase[0] in i:
					#print "index du debut de la derniere phrase"
					index = result_tag.index(i)
					#print index
					tag_dernier = result_tag[index:]
			
			#print tag_dernier
			if tag_dernier!=None :
				sentiments_dernier = self.calcul_polarity_score(tag_dernier)
			else :
				return -1

			if sentiments_dernier["polarity"]<0:
				return 1
			else :
				return -1





	#En utilisant la base FEEL, on peut simplement déterminer la négativité/positivité générale du tweet/ensemble de phrase. 		
	def calcul_polarity_score(self,tagged_text):
		sentiment_gather = []
		for mono_tag in  tagged_text:
			inflex = mono_tag[2].replace("\r","")
			#print inflex
			if inflex in asciifeel:
				#print feel.columns.name
				feel.ix[asciifeel.index(inflex),:].values

				sentiment_gather.append(feel.ix[asciifeel.index(inflex),:].values)
		
		score_sentiment = {"polarity":0,"joy":0,"fear":0,"sadness":0,"anger":0,"surprise":0,"disgust":0}
		polarity=float(0)
		sentiment_impact = [j for j in sentiment_gather if 1 in j[3:8]]
		for i in sentiment_impact :
			
			score_sentiment["joy"] = score_sentiment["joy"]+i[3]
			score_sentiment["fear"] = score_sentiment["fear"]+i[4]
			score_sentiment["sadness"] = score_sentiment["sadness"]+i[5]
			score_sentiment["anger"] = score_sentiment["anger"]+i[6]
			score_sentiment["surprise"] = score_sentiment["surprise"]+i[7]
			score_sentiment["disgust"] = score_sentiment["disgust"]+i[8]

			if i[3]>0:
				sumi = float(i[3])/float(2)
				polarity= polarity + sumi/float(len(sentiment_impact))
			if 1 in i[4:6] or i[8]>0:
				sumi = i[4]+i[5]+i[6]+i[8]
				sumi = float(sumi)/float(4)
				polarity = polarity- float(sumi)/float(len(sentiment_impact))

			if polarity <0:
				polarity = polarity- 0.5*i[7]/float(len(sentiment_impact))
			else :
				polarity = polarity+ 0.5*i[7]/float(len(sentiment_impact))
		
		score_sentiment["polarity"]=polarity
		#print "sentiment_values :"
		#print score_sentiment
		return score_sentiment


	#fonction qui regroupe les tweets/vdm extraits des différents sites webs 
	def gather_all_vdm(self):
		try:
			file = codecs.open("Data_apprentissage/vdm_unitaire.txt", "r")
		except IOError:
			msg = "Unable to create file on disk."
			return 0
		print file
		soup = bs4.BeautifulSoup(file, 'lxml')

		infos = {"post":[], "class":[]}
		#print soup
		for i in soup.find_all("vdm_unit"):
			#print i
			infos["post"].append({"content":str(i)})
			infos["class"].append(0)
		file.close()
		try:
			file2 = codecs.open("Data_apprentissage/vdm_non_unitaires.txt", "r", "utf-8")
		except IOError:
			msg = "Unable to create file on disk."
			return 0

		print file2
		soup2 = bs4.BeautifulSoup(file2, 'lxml')
		#print soup

		for j in soup2.find_all("vdm_non_unit"):
			#print i
			infos["post"].append({"content":str(j)})
			infos["class"].append(1)

		file2.close()

		try:
			file3 = codecs.open("Data_apprentissage/non_vdm.csv", "r", "utf-8")
		except IOError:
			msg = "Unable to create file on disk."
			return 0

		print file3
		#LXML plante car trop gros : 
		soup3 = bs4.BeautifulSoup(file3, 'html.parser')
		last =""
		#print len (infos["post"])
		#print len (soup3.find_all("non_vdm"))
		#return 0
		for k in soup3.find_all("non_vdm"):
			infos["post"].append({"content":str(k)})
			infos["class"].append(1)
			last = k
		#print infos
		
		file3.close()
		#return 0
		#On fait 5000
		infos["post"]=infos["post"][:2500]
		infos["class"]=infos["class"][:2500]

		print len(infos["post"])
		print len(infos["class"])

		return infos
		#print classifier.liste_article
		#classifier.find_variable_vdm()

def main():
	classifier = Classifier()
	classifier.get_bootstrap_testing_data()

if __name__ == '__main__':
 	main()
	pass