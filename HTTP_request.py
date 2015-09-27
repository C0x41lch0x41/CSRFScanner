#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Module gerant les requetes HTTP"""

import httplib
import sys
import socket
import handle_html
import comparison_method


def resolve_url(url):
	"""Permet d'obtenir l'adresse IP a partir
	de l'url. Cette fonction n'est pas utilisee, la
	resolution est effectuee automatiquement par la 
	librairie http
	Argument : - string url : adresse complete de la page
	Return : - string adresse IP
	"""
	return socket.gethostbyname(url)

	
def send_request(host, pagename, cookie=""):
	"""Envoi une requete HTTP GET avec ou sans cookie
	Arguments : - string host : site web
				- string pagename : nom de la page
				- string cookie : cookie d'authentification
	Return : - objet httplib.HTTPResponse 
	"""
	connection = httplib.HTTPConnection(host)		
	if cookie == "":
		connection.request("GET", pagename)
	else:
		head_cookie={"Cookie": cookie}
		connection.request("GET", pagename, headers=head_cookie)
	response = connection.getresponse()
	return response


def handle_redirect(response, host, pagename, cookie=""):
	"""Gere les redirections du type 302 Redirect ou 302 Moved temporarily
	Utile si l'utilisateur entre une url du type http://www.monsite.fr. Ici seul le host est renseigne.
	Suivant la configuration du serveur web, le client peut recevoir un message de redirection
	Arguments : - objet httplib.HTTPResponse : reponse susceptible d'etre une redirection
				- string host : site web
				- string pagename : nom de la page
				- string cookie : cookie d'authentification
	Return : - objet httlib.HTTPResponse : reponse une fois les redirections effectuees
	"""
	while response.status == 302:
		host_pagename = {}
		headers = response.getheaders()
		
		#l'adresse de la redirection se trouve dans le champ location du header HTTP
		new_location = [location for name, location in headers if name == "location"][0]
		intern_or_relative = which_kind_of_link(host, new_location)
		if intern_or_relative == 0 or intern_or_relative == 1:
			host_pagename = handle_html.url_to_host_pagename(new_location)
		elif intern_or_relative == 2:
			host_pagename["host"] = host
			host_pagename["pagename"] = new_location
		elif intern_or_relative == 3:
			host_pagename["host"] = host
			host_pagename["pagename"] = handle_html.get_absolute_path(pagename)+new_location
		else:
			break
		
		response = send_request(host_pagename["host"], host_pagename["pagename"], cookie)
		
	return response
	
	
def get_html_response(host, pagename, cookie=""):
	"""Utilise send_request et handle_redirect
	pour retourner le code HTML d'un host et d'un nom de page passee en argument
	Arguments : - string host : host du site contenant la page
				- string pagename : nom de la page
				- string cookie : cookie d'authentification
	Return : - string : le code HTML de la page sous la forme d'une chaine de caracteres
	"""
	response = send_request(host, pagename, cookie)
	response = handle_redirect(response, host, pagename,cookie)
	return handle_html.process_html_string(response.read())
	
	
def get_all_intern_link(host, cookie, list_link, index):
	"""Retourne tous les liens internes d'un site web.
	Pour cela une premiere page HTML est analysee, tous les liens interne
	sont ajoutes a la liste qui sera retourne. Chaque lien est ensuite analyse
	a son tour. On fait attention a ne pas rajouter un lien qui existe deja dans la liste
	Arguments : - string host : host du site
				- string cookie : cookie d'authentification
				- string list_link : liste contenant l'ensemble des liens a tester
				- int index : index du lien a tester dans la liste
	"""
	buff_list = []
	string = get_html_response(host, list_link[index], cookie)
	absolute_path = handle_html.get_absolute_path(list_link[index])
	buff_list = handle_html.extract_intern_link(string, host, absolute_path)
	list_link = comparison_method.diff_list(list_link, buff_list)
		
	if index == len(list_link) - 1:
		return
	get_all_intern_link(host, cookie, list_link, index + 1)
	
	
def main_http():
	"""Fonction servant a tester le module HTTP_request
	Le code HTML de la page demandee est imprime sur la sortie standard
	"""
	if len(sys.argv) == 2 or len(sys.argv) == 3:
		host_pagename = {}
		host_pagename = handle_html.url_to_host_pagename(sys.argv[1])
		#Sans cookie d'authentification
		if len(sys.argv) == 2:
			response_html = get_html_response(host_pagename["host"], host_pagename["pagename"])
			print response_html	
		#Avec cookie d'authentification
		else:
			response_html = get_html_response(host_pagename["host"], host_pagename["pagename"], sys.argv[2])
			#print response_html
			tree = handle_html.build_tree(response_html)
			handle_html.print_tree(tree)
	else:
		print "== [Utilisation] ./HTTP_request.py URL [Cookie] =="
			
					
if __name__ == "__main__":
	main_http()
	
		