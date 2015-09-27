#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Module gerant toutes les methodes de comparaisons"""

import sys
import handle_html


def rdiff(stringA, stringB):
	"""Implementation python de la methode rdiff
	Arguments : - string stringA : premier string a comparer
				- string stringB : second string a comparer
	Return : - int : 
					- 0 : stringA et stringB sont differents
					- 1 : stringA et stringB sont identiques
	"""
	if stringA == stringB:
		return 1
	return 0
	
	
def rdiff_tree(treeA, treeB, bufftree):
	"""Applique la methode rdiff a deux arbres
	Arguments : - objet Node treeA : premier arbre a comparer
				- objet Node treeB : second arbre a comparer
				- objet Node bufftree : arbre servant a bufferiser l'arbre qui sera retourne. 
										Il est passe en argument pour que la recursivite puisse
										avoir lieu en gardant en memoire l'etat de la comparaison
	Return : - objet Node : Un arbre contenant tous les noeuds commun a treeA et treeB
	"""
	if treeA.child != []:
		for i in range(len(treeA.child)):
			if i < len(treeB.child) and rdiff(treeA.child[i].value, treeB.child[i].value) == 1:
				bufftree.add_child(value=treeA.child[i].value)
				#La recursivite a lieu ici
				#Un enfant vient d'etre rajoute a bufftree. On relance donc la fonction
				#sur cet enfant qui est le dernier de la liste (d'ou bufftree.child[len(bufftree.child) - 1])
				rdiff_tree(treeA.child[i], treeB.child[i], bufftree.child[len(bufftree.child) - 1])
	return bufftree
	
	
def diff_treeform(treeformA, treeformB):
	"""Fais la difference des deux arbres passes en argument. Les deux arbres ne contiennent que 
	des formulaires. Par exemple : - root
										- form1
											- champ1.1
											- champ1.2
										- form2
											- champ2.1
												- souschamp2.1.1
											- champ2.2
											- champ2.3
	Ainsi les enfants du noeud root ne sont que des formulaires.
	Chaque arbre passe en argument doit avoir un noeud principal root
	La difference se fait suivant l'algorithme :
		- Si tous les champs d'un formulaire du premier arbre sont identiques a tous les champs d'un
		formulaire du second alors ne rien faire
		- Sinon ajouter le formulaire a l'arbre qui sera retourne en resultat
	Arguments : - objet Node treeformA : arbre dont on cherche les formulaires qui ne sont pas 
										 dans le second argument
				- objet Node treeformB : arbre qui contient les formulaires dont on ne veut pas
	Return : - objet Node : arbre contenant tous les formulaires de treeformA qui ne sont pas
							dans treeformB
	"""
	bufftree = handle_html.Node("root")
	for i in range(len(treeformA.child)):
		count = 0	
		if len(treeformB.child) == 0:
			return treeformA
		for j in range(len(treeformB.child)):
			#si les formulaires ne sont pas strictement egaux
			if treeformA.child[i].is_equal(treeformB.child[j]) == 0:
				count = count + 1
		#si le nombre de formulaire qui ne sont pas egaux est egale
		#au nombre d'enfant de treeformB alors c'est que le formulaire
		#de treeformA ne se trouve pas dans treeformB
		if count == len(treeformB.child):
			bufftree.add_child(node=treeformA.child[i])
	return bufftree
	
	
def diff_list(listA, listB):
	"""Ajoute tous les elements de la seconde liste
	qui ne sont pas dans la premiere a la premiere
	Arguments : - list listA : premiere liste
				- list listB : seconde liste
	Return : - list : liste avec tous les element de listA et tous ceux
					  de listeB qui ne sont pas dans listA
	"""
	for i in range(len(listB)):
		if listB[i] not in listA:
			listA.append(listB[i])
	return listA
				

def main_comparison_method():
	"""Fonction servant a tester le module comparison_method.
	Le code HTML des deux fichiers passes en argument du module
	est parse dans deux arbres respectifs. Ces deux objets
	sont ensuite compares pour ne garder que les champs en commun.
	Finalement les formulaires de l'arbre en commun sont extraits
	et imprime sur la sortie standard
	"""
	if len(sys.argv) == 3:
		bufftree_comp = handle_html.Node("root")
		bufftree_form = handle_html.Node("root")
		stringA = handle_html.read_file(sys.argv[1])
		stringB = handle_html.read_file(sys.argv[2])
		treeA = handle_html.build_tree(stringA)
		treeB = handle_html.build_tree(stringB)
		bufftree_comp = rdiff_tree(treeA, treeB, bufftree_comp)
		bufftree_form = handle_html.extract_form(bufftree_comp, bufftree_form)
		handle_html.print_tree(bufftree_form)
	else:
		print "== [Utilisation] ./comparison_method.py filenameA filenameB =="
	
	
if __name__ == "__main__":
	main_comparison_method()