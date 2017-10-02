# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from contextlib import closing
from urllib2 import urlopen
import urllib2
import nltk
import lxml
import requests
from unidecode import unidecode
import unicodedata
import re
import time
from nltk.stem import SnowballStemmer
from datetime import datetime
import json

#Traduction necessaire et sans accent des mois en FR
month_fr = ["janvier", "fevrier", "mars", "avril", "mai", "juin", "juillet", "aout","septembre","octobre","novembre","decembre"]


def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')

def format_date(string) :
	split = string.split("\n")
	try :
		tokens = split[2]
		tokens = nltk.word_tokenize(tokens)
		res=""+tokens[3]+"-"+str(month_fr.index(tokens[2])+1)+"-"+tokens[1]+"T"+tokens[4]+":00Z"
	except :
		return string

	return res


#Class s'occupant de l'extraction de l'information sur VDM
class Extractor :

	def __init__(self, nb_article=1):
		self.page=1
		self.index = 0
		self.nb_article=nb_article
		self.keyword=""
		self.json_stockage= {"post":[], "count":0 }
		self.encoding='utf-8'
		self.all_links= [""]
		




	def extractArticleListToExplore(self,p):
		#Test est-ce qu'on extrait correctement? 
		#Test est-ce qu'on fait en sorte qu'il y ait 200 articles? 

		#Permet de ne pas surcharger le serveur
		time.sleep(0.5)

		#keyword = strip_accents(keyword.decode("utf8"))
		address = "http://www.viedemerde.fr/news"+"?page="+str(p)
		#tokens = nltk.word_tokenize(keyword)

		headers = {"Host":" www.viedemerde.fr",
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Encoding': 'gzip, deflate, br',
		'Accept-Language': 'fr,fr-FR;q=0.8',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'
		}

		

		#print(address)

		try:
			#website = urllib2.urlopen(address)
			with requests.Session() as s:
				reqs = s.get(address, headers=headers)
			#reqs = requests.get(address, headers=headers)
		    #print(website.read())
		except requests.exceptions.RequestException as e: 
			print e
			return -1

		

		soup = BeautifulSoup(reqs.text, 'lxml')
		#print(len(soup.find_all("article")))
	    #	print(tag.name)

		search_tag =""
		#Recupere tous les liens des articles sur chaque page (environ 30+)
		for article in soup.find_all('article'):
			if  len(self.all_links)>=self.nb_article:
				continue
			for link in article.find_all('a'):
				if link.get("href") is None:
					continue
				if "/article" in link.get("href") and ".html" in link.get("href"):
					n_link = link.get('href')
					if n_link not in self.all_links:
						#print n_link
						self.all_links.append(n_link)

		#Il y a eu une erreur ou un changement, all_links est vide.
		if p>=1 and len(self.all_links)==0:
			return -1

		#Sortie normale
		return len(self.all_links) 

	#forme du retour :	{'id':'','author':'', 'content':'', 'date':''}
	def exploreArticle(self,url=""):
		#On ne surcharge pas le serveur :
		time.sleep(0.05)

		result= {'id':'','author':'', 'content':'', 'date':''}
		if url not in self.all_links:
			return -1
		result["id"]= self.all_links.index(url)+1

		address = "http://www.viedemerde.fr"+url
		headers = {"Host":" www.viedemerde.fr",
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Encoding': 'gzip, deflate, br',
		'Accept-Language': 'fr,fr-FR;q=0.8',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'
		}
		

		try:
			with requests.Session() as s:
				reqs = s.get(address, headers=headers)

		except requests.exceptions.RequestException as e: 
			print e
			return -1
		
		soup = BeautifulSoup(reqs.text, 'lxml')

		#Recupere les auteurs 
		for author in soup.find_all("meta", attrs={'name': 'author'}):
			result['author']=author['content']

		#Recupere les articles et les dates
		for article in soup.find_all("article", class_="art-panel  "):
			s= ""
			for content in article.find_all("p"):

				s= s+" <br> "+strip_accents(content.text)
				s = s.replace("\'"," " )

			result["content"] = s

			for date in article.find_all('div', class_="text-center block"):
				print strip_accents(date.text)
				print "Patientez s'il vous plait. Progression : "+ str(result["id"])+"/"+str(len(self.all_links))
				result["date"]= format_date(strip_accents(date.text))


		return result

	def create_json(self, length=1):
		self.nb_article = length
		self.all_links=[]
		while len(self.all_links)<self.nb_article:
			l = self.extractArticleListToExplore(self.page)
			if l == -1:
				return -1
			self.page = self.page+1

		for url in self.all_links:
			self.json_stockage["count"]+=1
			self.json_stockage["post"].append(self.exploreArticle(url))
		


		return self.json_stockage
	

	def __str__(self) :
		return json.dumps(self.json_stockage, indent=1)

	
def main():
	ex =  Extractor()
	ex.create_json(2)

	print(ex)




	#print(extractInfoBetweenKw(keyword[0], keyword[1]))

if __name__ == '__main__':
 	#main()
 	main()