# -*- coding: utf-8 -*-

import nltk as nltk
import re
import math as math
from unidecode import unidecode
import json
from flask import request
from flask import abort
from flask import Flask, jsonify
from flask import make_response

from dicttoxml import dicttoxml
import dateutil.parser
import datetime


import extractor
import form

app = Flask(__name__)

#On definit l'extracteur :
ex = extractor.Extractor()
#Notre BDD :)
infos={}

#Nombre de post extraits
nb_posts =200

#Nb test de la request "fetch":
nb_test=3

# Mini-interface pour fetch :
def fetch_it():
	actual_test =0
	request = ""
	request_ask = form.Form()

	while request != "fetch" and actual_test<nb_test:
		request = request_ask.request_form()
		actual_test = actual_test+1
	
	if actual_test>= nb_test:
		return -1
	else :
		return request

# Rend un peu plus beau le JSON affiche dans la page html
def prettify_json_in_html_page(pretty_json_string):
	return re.sub(r"\n", "<br>", pretty_json_string)

#Fonction retournant si check_date est entre s(tart)_date & e(nd)_date 
def is_between_time(s_date, e_date, check_date):
	s_date = s_date.replace("Z","")
	s_date = s_date.replace("T", " ")

	e_date = e_date.replace("Z","")
	e_date = e_date.replace("T", " ")


	check_date = check_date.replace("Z","")
	check_date = check_date.replace("T", " ")

	try : 
		s_parsed = dateutil.parser.parse(s_date)
		e_parsed = dateutil.parser.parse(e_date)
		check_parsed = dateutil.parser.parse(check_date)
	except:
		return False

	if s_parsed <= check_parsed <= e_parsed: 
		return True
	else:
		return False


#Accès par defaut dans l'url locale
@app.route("/")
def helloworld():
	return "Hi ! Welcome to this Flask Mini-Server ! \n \nIf you want to do something, use your local_url/api/posts, to access to all the post in a very raw way. I had fun creating this !"

#Montre toute la liste de post
@app.route("/api/posts", methods=['GET'])
def show_extracted_info():
	#print(infos)
	try:
		#xml = dicttoxml(infos, custom_root='test', attr_type=False)
		j_dump = json.dumps(infos, indent=2)
		print(j_dump)
	except:
		print "error ", sys.exc_info()[0]

	return prettify_json_in_html_page(j_dump)
	#return xml

#Acces par ID directement
@app.route('/api/posts/<int:post_id>', methods=['GET'])
def select_id_post(post_id):
	#print post_id
	try:
		posts = [post for post in infos["post"] if post['id'] == post_id]
	except :
		print("erreur dans l'extraction d'infos")
		abort(500)

	if len(posts) == 0:
		abort(404)


	return prettify_json_in_html_page(json.dumps(({'post': posts}), indent=2))

#Acces par date
@app.route('/api/posts/from=<s_date>&to=<e_date>', methods=['GET'])
def select_by_date(s_date, e_date):
	try:
		posts=[post for post in infos["post"] if is_between_time(s_date,e_date, post["date"])]
	except:
		print("erreur dans l'extraction d'infos")
		abort(500)

	if len(posts) == 0:
		abort(404)

	return prettify_json_in_html_page(json.dumps(({'post': posts}), indent=2))

#acces par auteur
@app.route("/api/posts/author=<author>", methods=['GET'])
def select_by_author(author):
	try :
		posts = [post for post in infos["post"] if post['author'] == author]
	except:
		print("erreur dans l'extraction d'auteur")
		abort(500)
	if len(posts) == 0:
		return "Pas de résultat, essayez avec l'auteur : " + str(infos["post"][0]["author"])

	return prettify_json_in_html_page(json.dumps(({'post': posts}), indent=2))

#Gestion des erreurs d'adresse
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(500)
def not_found(error):
    return make_response(jsonify({'error': 'Probleme serveur'}), 500)





#Lance l'appli
#1) Request de la petite commande
#2) Extraction des informations
#3) Server avec acces REST
def launch():
	#1)

	#fetch_it()
	#2)
	infos = ex.create_json(nb_posts)
	#3)
	app.run()



if __name__ == "__main__":
	#1)
	# Malheureusement, j'ai pas reussi à le faire marcher avec Docker
	u_input = fetch_it()

	if u_input != -1:
		#2)
		infos = ex.create_json(nb_posts)
		#3)
		app.run()
	else :
		print "app cancel"