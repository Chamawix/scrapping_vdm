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

french_stops = set(stopwords.words('french'))




encoding = "utf-8"


'''NLTK 3.0 offers map_tag, which maps the Penn Treebank Tag Set to the Universal Tagset, a course tag set with the following 12 tags:

VERB - verbs (all tenses and modes)
NOUN - nouns (common and proper)
PRON - pronouns
ADJ - adjectives
ADV - adverbs
ADP - adpositions (prepositions and postpositions)
CONJ - conjunctions
DET - determiners
NUM - cardinal numbers
PRT - particles or other function words
X - other: foreign words, typos, abbreviations
. - punctuation

We'll map Stanford's tag set to this tag set then compare the similarity between subregions of French and English sentences.'''




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

class Classifier :

	#On passe la liste des articles extrait dans le init
	def __init__(self, liste_article):
		self.mot_clef_max = 3
		self.liste_article = liste_article
		self.extract_example = {}
		
		#self.morphalou=pd.read_table("Dictionnaire/Morphalou.csv", dtype=None, delimiter =',',header = 0, encoding = encoding)
		#self.stemmer = SnowballStemmer("french")

		self.training_set = None


	def find_variable_vdm(self):
		moyenne_nb_proposition = 0

		for i in self.liste_article["post"]:
			soup = bs4.BeautifulSoup(i["content"], 'lxml')
			clean_text = soup.get_text()

			tokens = wordpunct_tokenize(clean_text)
			text= nltk.Text(tokens)

			words = [w.lower() for w in text]
			vocab = sorted(set(words))

			#stem_tok = [self.stemmer.stem(i) for i in tokens[3:]]


			nb_propositions = re.split("(?:"+"(?:"+" | ".join(str(x) for x in dico["CONJ"])+")"+"|"+"(?:"+"|".join(str(x) for x in ["\.", "\.\.", "\.\.\.", "\?","\!"])+"))",clean_text)
			
			for i in nb_propositions:
				if re.search("VDM(?! *\w+)", i) !=None or re.search("(?!\w)(?:"+" *| *".join(str(x) for x in dico["PREP"])+") (?!\w)", i.lower()) != None or  "" ==i:
					nb_propositions.remove(i)



			nb_phrase = re.split("(?:"+"|".join(str(x) for x in ["\.", "\.\.", "\.\.\.", "\?","\!"])+")", clean_text)
			for i in nb_phrase:
				if re.search("VDM(?! *\w+)", i) !=None or ""==i:
					nb_phrase.remove(i)
			
			print clean_text

			print len(nb_phrase)
			if len(nb_phrase)>1:
				#Taille en mot de la dernière proposition, est ce une chute? 
				print len (wordpunct_tokenize((nb_phrase[len(nb_phrase)-1])))


			#print len(nb_propositions)
			#print [ i for i in tokens if i in dico["CONJ"]]
			#print [pos_tag(word_tokenize(i)) for i in nb_propositions]





def main():

	file = codecs.open("vdm_unitaire.txt", "r", "utf-8")
	soup = bs4.BeautifulSoup(file, 'lxml')

	infos = {"post":[]}
	#print soup
	for i in soup.find_all("vdm_unit"):
		#print i
		infos["post"].append({"content":str(i)})

	classifier = Classifier(infos)
	#print classifier.liste_article
	classifier.find_variable_vdm()

	file.close()



if __name__ == '__main__':
 	main()
	pass