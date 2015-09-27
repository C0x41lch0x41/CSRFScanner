#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Module principal permettant de lancer le programme"""

import sys
import comparison_method
import handle_html
import HTTP_request

class StringParam:
	"""Classe representant un string. Utiliser un objet
	StringParam plutot qu'un string permet de le passer
	en parametre resultat aux fonctions
	"""

	def __init__(self, value=""):
		"""Constructeur de la classe StringParam
		Argument : - string value : valeur a donner au StringParam
		"""
		self.value = value
		

def from_list_to_treeform(list_tree):
	"""Applique la methode rdiff aux deux arbres passes en argument
	et extrait les formulaires du resultat
	Argument : - list list_tree : liste contenant deux elements :
															- objet Node list_tree[0] : arbre cree a partir d'une premiere requete HTTP
															- objet Node list_tree[1] : arbre cree a partir d'une seconde requete HTTP
															                            sur la meme page HTML
	Return : - objet Node : arbre contenant les formulaires statiques des deux arbres passes en argument
	"""
	tree_comp = handle_html.Node("root")
	tree_form = handle_html.Node("root")
	tree_comp = comparison_method.rdiff_tree(list_tree[0], list_tree[1], tree_comp)
	tree_form = handle_html.extract_form(tree_comp, tree_form)
	return tree_form


def proceed_two_HTTP_request(host, pagename, cookie="", string_html=None):
	"""Execute deux requetes HTTP a destination de la meme url avec ou sans cookie et
	retourne un arbre contenant les formulaires statiques de l'url.
	Deux plus, cette fonction peut retourner le code HTML de la page dans un string
	Arguments : - string host : host du site contenant la page
				- string pagename : nom de la page
				- string cookie : cookie d'authentification
				- objet StringParam string_html : objet accueillant le code HTML de la page
	Return : objet Node : arbre contenant les formulaires statiques de la page se trouvant a l'adresse url
	"""
	list = []
	for i in range(2):
		response_html = HTTP_request.get_html_response(host, pagename, cookie)
		tree = handle_html.build_tree(response_html)
		list.append(tree)
	
	if string_html != None:
		string_html.value = response_html	
	return from_list_to_treeform(list)
	

def get_form_from_url(cookie, url="", host="", pagename=""):
	"""Effectue 4 requetes HTML aupres de la page passee en argument du programme.
	Deux requetes sans cookie et deux requetes avec.
	Les formulaires statiques sont extraits et compares.
	Finalement seul les formulaires statiques apparaissant dans un 
	contexte authentifie sont imprimes sur la sortie standard.
	La page peut etre passee soit avec l'url complete soit directement
	avec le host et le nom de la page (ceci pour pouvoir etre utilise
	aussi bien avec le mode recursif que statique).
	Arguments : - string cookie : cookie d'authentification
				- string url : url complete de la page
				- string host : host du site contenant la page
				- string pagename : nom de la page
	"""
	host_pagename = {}
	string_html = StringParam()
	
	if url != "":
		host_pagename = handle_html.url_to_host_pagename(url)
	elif host != "":
		host_pagename["host"] = host
		host_pagename["pagename"] = pagename

	treeform_guest = proceed_two_HTTP_request(host_pagename["host"], host_pagename["pagename"])
	treeform_user = proceed_two_HTTP_request(host_pagename["host"], host_pagename["pagename"], cookie, string_html)
	final_tree = comparison_method.diff_treeform(treeform_user, treeform_guest)
	
	if len(final_tree.child) != 0:
		print "<h1>*** Pour la page : "+host_pagename["host"]+host_pagename["pagename"]+" ***</h1>"
		handle_html.print_form(final_tree, string_html.value)
	else:
		print "<h1>*** Aucun formulaire pour la page : "+host_pagename["host"]+host_pagename["pagename"]+" ***</h1>"
	
	print "\n"	
		

def main():
	"""Fonction principale du programme. Deux modes peuvent etre utilises : 
															- recursif avec l'option -R
															- statique sans option
	Dans le mode recursif, l'ensemble des liens interne du site sont d'abord recherches et 
	sauvegardes dans une liste. Ensuite l'analyse est lancee sur chaque membre de la liste.
	En mode statique seul l'url passe en argument est analyse
	"""
	usage = "== [Utilisation] ./main.py [-R] URL Cookie"
	if len(sys.argv) == 4:
		if sys.argv[1] == "-R":
			host_pagename = {}
			list_link = []
			url = sys.argv[2]
			cookie = sys.argv[3]
			host_pagename = handle_html.url_to_host_pagename(url)
			list_link.append(host_pagename["pagename"])
			HTTP_request.get_all_intern_link(host_pagename["host"], cookie, list_link, 0)
			for i in range(len(list_link)):
				get_form_from_url(cookie=cookie, host=host_pagename["host"], pagename=list_link[i])
		else:
			print "Invalide option "+sys.argv[1]
			print usage
	elif len(sys.argv) == 3:
		cookie = sys.argv[2]
		url = sys.argv[1]
		get_form_from_url(cookie=cookie, url=url)
	else:
		print usage 
	

if __name__ == "__main__":
	main()