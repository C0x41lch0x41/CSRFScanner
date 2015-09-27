#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Module gerant le parsage du langage HTML"""

import sys
import re


class Node:
	"""Classe representant un arbre.
	Un arbre (ou noeud) est compose de :
									- string value : valeur du noeud
									- list child : liste des noeuds enfant
	Cette classe implemente les methodes :
									- add_child : ajoute un enfant a la fin de la liste
									- remove_child : supprime un enfant a un index precis
									- is_equal : permet de savoir si l'arbre est identique
												 a un autre
	"""
	
	def __init__(self, value=""):
		"""Constructeur de la classe. Un noeud par defaut n'a pas d'enfant
		et est son propre parent.
		Argument : - string value : valeur du noeud a construire
		Return : - objet Node : noeud sans enfant, etant son propre pere et ayant la valeur value
		"""
		self.value = value
		self.child = []
		self.parent = self
		
	def add_child(self, value="", node=None):
		"""Ajoute un enfant a la fin de la liste des enfants du noeud.
		L'ajout d'un enfant peut se faire de deux manieres :
														- En precisant la valeur. L'enfant cree n'aura
														  donc pas d'enfant
														- En precisant le noeud. L'enfant cree sera
														  le noeud passe en argument
		Arguments : - string value : valeur du noeud enfant si ajout par valeur
					- objet Node node : le noeud a ajouter si ajout par noeud
		"""
		if node == None:
			child = Node(value)
		else:
			child = node
		child.parent = self
		self.child.append(child)
	
	def remove_child(self, index):
		"""Efface de la liste l'enfant se situant a l'index passe en arguement
		Argument : - int index : index de l'enfant a effacer
		"""
		del self.child[index]
		
	def is_equal(self, tree):
		"""Permet de savoir si le noeud est identique a un autre passe
		en argument. Deux noeuds sont egaux si :
											- leurs valeurs sont egales
											- ils ont le meme nombre d'enfants
											- chaque enfant du noeud est identique a l'enfant
											  du noeud passe en argument qui se situe a la 
											  meme position
		Argument : - objet Node tree : noeud a comparer
		Return : - int :
					    - 0 : les noeuds ne sont pas egaux
						- 1 : les noeuds sont egaux
		"""
		if self.value != tree.value or len(self.child) != len(tree.child):
			return 0
		for i in range(len(self.child)):
			if self.child[i].is_equal(tree.child[i]) == 0:
				return 0
		return 1


def url_to_host_pagename(url):
	"""Convertie l'url complet de la page en host
	et nom de la page au sein du site
	Exemple : url = http://www.monsite.fr/exemple.php
	host : www.monsite.fr
	nom de la page : exemple.php
	Argument : - string url : adresse complete de la page
	Return : - dictionnaire : 
							- Cle host : host
							- Cle pagename : nom de la page
	"""
	host_pagename = {}
	if url.startswith("http://"):
		url=url.lstrip("http://")
	
	buff_host_pagename = url.partition('/')
	#buff_host_pagename = ['www.monsite.fr', '/', 'exemple.php']
	
	host_pagename["host"] = buff_host_pagename[0]
	
	if len(buff_host_pagename[1]) != 0:
		host_pagename["pagename"] = buff_host_pagename[1]+buff_host_pagename[2]
	else:
		host_pagename["pagename"] = "/"
		
	return host_pagename
				

def from_value_to_nametag(value):
	"""Trouve le nom d'un tag a partir de sa 
	valeur complete.
	Exemple on passe a la fonction le tag suivant :
	"a id="id" href="http://www.google.fr" onclick="dosomething()""
	Ici le nom du tag est : "a"
	Argument : - string value : valeur complete du tag sans les balises '<' et '>'
	Return : - string : nom du tag 
	"""
	name = value.partition(' ')[0]
	return name

	
def move_score(value, score):
	"""A partir de la valeur d'un tag et d'un score,
	change le score suivant l'algorithme :
										- Si c'est un tag fermant (exemple : </a>) : reduire score de 1
										- Si ce n'est ni un tag fermant (</a>) ni un tag
										  ouvrant - fermant (<input src="img" type="image" />) : augmenter score de 1
										- Sinon (tag ouvrant - fermant) : ne rien faire
	Arguments : - string value : valeur complete du tag sans les balises '<' et '>'
				- int score : score a modifier
	Return : - int : score apres modification
	"""
	#tag fermant
	if value[0] == '/':
		score = score - 1
	#on test s'il ne s'agit pas d'un tag
	#ouvrant - fermant
	elif value[len(value) - 1] != '/':
		score = score + 1
		
	return score


def is_there_endtag(value, string_to_tree):
	"""Permet de determiner, a partir de la valeur complete d'un tag ouvrant
	et de l'ensemble du code HTML qui suit ce tag, si il y a bien le tag fermant 
	correspondant. Par exemple il arrive que les tags <br>, <li> ou <input> s'ouvre sans se fermer.
	Il faut alors leurs appliquer un traitement specifique.
	Pour determiner si il y a bien un tag fermant, on parcourt l'ensemble du code HTML a la recherche
	d'une balise <nom_du_tag> ou </nom_du_tag>. Pour chaque balise trouve, on change le score grace a la fonction
	move_score. Lorsque le score arrive a zero, on retourne la position de la balise dans le score.
	Si le score n'arrive jamais a zero, on retourne zero.
	Arguments : - string value : valeur complete du tag sans les balises '<' et '>'
				- string string_to_tree : l'ensemble du code HTML suivant le tag de valeur value
	Return : - int :
					- 0 : il n'existe pas de tag fermant correspondant
					- index : la position relative tu tag fermant dans le code           
	"""
	index = 0
	score = 1
	#on recupere la nom du tag
	name = from_value_to_nametag(value)
	name = re.escape(name)
	#on construit la regexp pour aller chercher les balises <nom_du_tag> ou </nom_du_tag>
	#dans la suite du code
	regexp = r"<"+name+r".*?>|</"+name+r">"
	match_tag = re.search(regexp, string_to_tree)

	#on parcourt l'ensemble du code HTML
	while match_tag != None:
		#on enleve les balises '<' et '>'
		value_tag = match_tag.group(0)[1:len(match_tag.group(0)) - 1]
		#on change le score en fonction de la balise trouvee
		#ceci est utile si a l'interieur d'un paragraphe HTML se trouve
		#un autre paragraphe avec le meme nom
		#par exemple : <a>
		#			     <b>
		#				   <a>Blabla</a>
		#				 </b>
		#			   </a>
		score = move_score(value_tag, score)
		index = index + match_tag.end()
		if score == 0:
			return index
		string_to_tree = string_to_tree[match_tag.end():]
		match_tag = re.search(regexp, string_to_tree)
	
	return 0


def find_right_close_char(string):
	"""A partir d'un code HTML sous forme de chaines 
	de caracteres qui commence juste apres l'ouverture
	d'une balise (caractere '<'), trouve le bon '>'. Cela
	permet de ne pas se tromper lors de la presence de tag du type :
	<input type="text" name="bla" value="<a href='blabla.php'>BLOU</a>" />
	Argument : - string string : code HTML qui commence juste apres un caractere '<'
	Return : - int : l'index du bon caractere '>' au sein du code
	"""
	score = 1
	start_pos = 0
	regexp = re.compile(r"<|>")
	while start_pos < len(string):
		match_char = regexp.search(string, start_pos)
		if match_char.group(0) == "<":
			score = score + 1
		else:
			score = score - 1
		
		if score == 0:
			return match_char.start() + 1
			
		start_pos = match_char.start() + 1
	
	return -1
	
	
def read_file(filename):
	"""Lit l'ensemble du fichier dont le nom est passe
	en argument et le retourne dans un string.
	Il s'agit d'une fonction de debug pour lire du code HTML directement
	a partir d'un fichier
	Argument : - string filename : nom du fichier
	Return : - string : le contenu du fichier
	"""
	file = open(filename, 'r')
	string = file.read()
	return string
	
	
def process_html_string(string):
	"""Permet de supprimer les commentaires ainsi que les scripts d'un code HTML
	pour ne pas que ceux-ci fausse la construction de l'arbre a partir du code.
	Argument : - string string : code HTML sous forme de string
	Return : - string : code HTML sans les commentaires
	"""
	#string = string.replace('\n', '')
	regexp = re.compile(r"<!--.*?-->", re.DOTALL)
	string = re.sub(regexp, "", string)
	regexp = re.compile(r"<script.*?>.*?</script>", re.DOTALL)
	string = re.sub(regexp, "", string)
	return string
	
	
def build_tree(string_to_tree):
	"""Construit un arbre a partir d'un code HTML sous forme de string.
	Le code HTML est parcourut lineairement et l'arbre est 
	construit suivant l'algorithme :
								- Tant que le code HTML n'a pas ete parcourut entierement :
											- Si le premier caractere est '<' :
																			- S'il s'agit d'un tag fermant (second caractere '/') : le noeud en cours devient son parent
																			- Sinon on ajoute le tag comme enfant au noeud courant et :
																				- S'il s'agit d'un tag ouvrant et s'il existe un tag fermant correspondant
																				  au tag ouvrant, le noeud courant devient l'enfant qui vient d'etre ajoute
										    - Sinon, on ajoute le string qui se trouve entre les deux tags comme enfant du noeud courant
											- On enleve le tag qui vient d'etre traite au code HTML
	Argument : - string string_to_tree : code HTML a partir duquel l'arbre est construit
	Return : - objet Node : l'arbre correspondant au code HTML
	"""
	tree = Node("root")
	buffnode = tree
	while string_to_tree != "":
		
		string_to_tree = string_to_tree.strip()
		
		#debut d'un tag
		if string_to_tree[0] == '<':
		
			index = find_right_close_char(string_to_tree[1:])
			
			#tag fermant
			if string_to_tree[1] == '/':
				buffnode = buffnode.parent
			else:
				#tag ouvrant - fermant
				if string_to_tree[index - 1] == '/':
					buffnode.add_child(value=string_to_tree[0:index + 1])
				#tag ouvrant
				else:
					buffnode.add_child(value=string_to_tree[0:index + 1])
					value_tag = string_to_tree[1:index]
					#on verifie qu'il existe un tag fermant
					#sans cette verification cela peut decaler 
					#l'ensemble de l'arbre
					if is_there_endtag(value_tag, string_to_tree[index + 1:]) != 0:
						buffnode = buffnode.child[len(buffnode.child) - 1]
					
			string_to_tree = string_to_tree[index + 1:]
			
		#on est dans le cas d'un string entre deux tags
		#par exemple : string_to_tree = Blabla</a> (le tag <a> a ete traite au-dessus)	
		else:
			index = string_to_tree.find('<')
			if index != -1:
				buffnode.add_child(value=string_to_tree[0:index])
				string_to_tree = string_to_tree[index:]
			#Si index = -1 c'est que le code HTML n'est pas bien fini,
			#Des caracteres subsistent a la fin sans aucune balise
			else:
				buffnode.add_child(value=string_to_tree)
				string_to_tree = ""
	
	return tree
			
			
def print_tree(tree):
	"""Imprime un arbre sur la sortie standard.
	Chaque noeud est imprime avec son parent.
	Il s'agit d'une fonction de debug permettant de
	verifier qu'un arbre a bien ete construit
	Argument : - objet Node tree : arbre a imprimer
	"""
	print tree.parent.value+"."+tree.value
	if tree.child == []:
		return
	for i in range(len(tree.child)):
		print_tree(tree.child[i])
		

def print_form(tree_form, string):
	"""Imprime les formulaires contenus dans l'arbre
	sur la sortie standard. Plutot que de faire la transformation
	inverse arbre - code HTML, on va chercher directement 
	dans le code HTML le formulaire correspondant.
	Arguments : - objet Node tree_form : arbre ne contenant que les formulaires a imprimer
				- string string : string contenant l'ensemble du code HTML de la page web en cours de traitement
	"""
	for i in range(len(tree_form.child)):
		size_value = len(tree_form.child[i].value)
		#on cherche le debut du formulaire dans le code HTML a partir de la valeur complete de ce dernier.
		#La valeur complete est la chaine de caractere compris entre les balises '<' et '>' d'un formulaire
		#exemple : value = "form method="get" action="action.php" name="Name""
		index_debut = string.find(tree_form.child[i].value)
		buff_string = string[index_debut:]
		#on se sert de is_there_endtag pour trouver la fin du formulaire dans le code HTML
		index_fin = is_there_endtag(tree_form.child[i].value[1:size_value - 1], buff_string[size_value:])
		index_fin = index_fin + size_value
		if index_fin != 0:
			print buff_string[0:index_fin]
			
		
def extract_form(tree_in, bufftree):
	"""Extrait tous les formulaires d'un arbre construit a partir
	de la reponse a une requete HTML. Des qu'un formulaire est trouve, on
	ne descend pas plus loin dans l'arbre, on ajoute l'ensemble du formulaire
	a l'arbre qui sera retourne en resultat
	Arguments : - objet Node tree_in : arbre contenant l'ensemble du code HTML et dont
									   on veut extraire les formulaires
				- objet Node bufftree : arbre auquel on ajoute chaque formulaire trouve, il sera 
										retourne en resultat
	Return : - objet Node : arbre contenant uniquement les formulaires
	"""
	for i in range(len(tree_in.child)):
		if tree_in.child[i].value.lower().startswith("<form ") is not True:
			#bufftree est utilise pour garder en memoire
			#l'etat du resultat lors de la recursivite
			extract_form(tree_in.child[i], bufftree)
		else:
			bufftree.add_child(node=tree_in.child[i])
	
	return bufftree


def which_kind_of_link(host, link):
	"""Permet de savoir quel est le type de lien
	Arguments : - string host : host du site
				- string link : lien a tester
	Return : int : 
					- -1 : le lien ne doit pas etre garde
					- 0  : le lien est un lien externe
					- 1  : le lien est un lien interne avec un chemin absolu complet (http://www.monsite/home/exemple.php)
					- 2  : le lien est un lien interne avec un chemin absolu (/home/exemple.php)
					- 3  : le lien est un lien interne relatif (exemple.php)
	"""
	if link == "":
		return -1
	#Si le lien contient le mot logout
	#on ne le traite pas pour de ne pas
	#faire expirer la session en cours
	if re.search(".*?logout.*?", link):
		return -1
	#Si le lien commence par feed, il
	#s'agit d'un lien qui permet d'ouvrir
	#une autre application sur l'ordinateur
	#client. On ne le traite pas
	if link.startswith("feed:"):
		return -1
	if link.startswith("https://"):
		return -1
		
	if link.startswith("http://") is not True and link.startswith("www.") is not True:
		if link[0] == '/':
			return 2
		else:
			return 3
		
	link = link.lstrip("http://")
	buff_host = link.partition('/')[0]

	if buff_host == host:
		return 1
	return 0
	
	
def get_absolute_path(pagename):
	"""Permet d'extraire le chemin absolu du nom
	d'une page. Exemple /exemple/index.php :
								- chemin absolu : /exemple/
	Argument : - string pagename : nom complet de la page
	Return : - string : chemin absolu
	"""
	#Pour chercher le chemin absolu,
	#on ne prend que l'url et pas les
	#arguments (ceux-ci se trouvent apres le caractere '?')
	pagename = pagename.partition('?')[0]
	partition_slash = pagename.rpartition('/')
	if partition_slash[0] == "":
		return pagename
	else:
		return partition_slash[0]+partition_slash[1]
	
	
def extract_intern_link(string, host, absolute_path):
	"""Extrait tous les liens d'un code HTML.
	Arguments : - string string : l'ensemble du code HTML
				- string host : host du site
				- string absolute_path : chemin absolu de la page
	Return : list : liste contenant tous les liens interne de la page HTML
	"""
	i = 0
	list_link = []
	list_link = re.findall(r"<a.*?href=.*?>", string)
	#la taille de la liste va etre amenee a changer
	#avec l'instruction del, d'ou l'utilite de while
	#par rapport a for
	while i < len(list_link):
		buff_string = list_link[i]
		buff_string = buff_string.strip('<>')
		buff_string = buff_string.split("href=")[1]
		buff_string = buff_string.split(" ")[0]
		buff_string = buff_string.strip('\'\"')
		intern_or_relative = which_kind_of_link(host, buff_string)
		if intern_or_relative == 1 or intern_or_relative == 2:
			list_link[i] = url_to_host_pagename(buff_string)["pagename"]
			i = i + 1
		elif intern_or_relative == 3:
			buff_string = absolute_path+buff_string
			list_link[i] = buff_string
			i = i + 1
		else:
			del list_link[i]
	
	return list_link 		
	

def main_parse_html():
	"""Fonction servant a tester les fonctions 
	du module handle_html.
	"""
	if len(sys.argv) == 2:
		#string = sys.argv[1]
		string = read_file(sys.argv[1])
		print process_html_string(string)
		#string_without_open_char = string[1:]
		#index = find_right_close_char(string_without_open_char)
		#print "Index : "+str(index)
		#print "Char : "+string[index]
		#print "String : "+string[:index]
	else:
		print "== [Utilisation] ./parse_html code_html =="
		

if __name__ == "__main__":
	main_parse_html()
	
	


		

