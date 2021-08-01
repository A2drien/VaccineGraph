#Imporations de divers modules
from operator import itemgetter
import matplotlib.pyplot as plt
import numpy as np


nom_fichier = "vacsi-a-fra-2021-07-30-19h09.csv"                                #Nom du fichier de données à traiter
limite_date_debut = "2021-02-02"                                                #Indique à partir de quelle date commence l'origine des données en format AAAA-MM-JJ (0 pour lever limite)
limite_nombre_jour = 0                                                          #Indique le nombre de dates à inscrire sur l'axe des abscisses (0 ou 1 conserve la liste)
limite_ecart_jour = 7                                                           #Indique le nombre d'espacement de dates (1 pour passer)

#Liste des objectifs
obj_1_dose = 50000000                                                           #50 000 000 primo-vaccinés
obj_tot_dose = 35000000                                                         #35 000 000 vaccinés
obj_50_ans_1_dose = 0.85                                                        #85% des +50 ans primo-vaccinés
obj_18_ans_1_dose = 0.75                                                        #75% des +18 ans primo-vaccinés
obj_18_ans_tot_dose = 0.66                                                      #66% des +18 ans complétement vaccinés

#Données sur la population (Insee, 2021) (https://www.insee.fr/fr/outil-interactif/5367857/details/20_DEM/21_POP/21C_Figure3#)
pop_50_ans = 27824662                                                           #27 824 662 Français ont plus de 50 ans
pop_18_ans = 53761464                                                           #53 761 464 Français ont plus de 18 ans


#Sert à limiter une liste à nb_element de manière uniforme
def reduction(liste):
    if limite_nombre_jour == 0 or limite_nombre_jour == 1: return liste         #nb_element ne doit pas être égal à 0 ou 1
    liste_compressee = []
    coeff = len(liste)/(limite_nombre_jour-1)                                   #Calcule l'écart idéal entre 2 éléments de la liste à compresser (prends en compte le premier et dernier élément)
    liste_compressee.append(liste[0])                                           #Ajoute le premier élement de la liste à compresser
    for i in range(len(liste)):
        if int(i/coeff) == len(liste_compressee):                               #Si la position de l'élément est supérieure ou égale à sa position dans la liste compressée
            liste_compressee.append(liste[i-1])                                 #Alors ajouter l'élement à la liste compressée
    liste_compressee.append(liste[-1])                                          #Ajoute le dernier élement de la liste dans la liste à compresser
    return liste_compressee

#Sert à formater les dates : "AAAA-MM-JJ" -> "JJ MMM"
def formatDate(date):
    date = date.rsplit("-")                                                     #Sépare la chaine en une liste de 3 éléments : [AAAA, MM, JJ]
    new_date = date[2]                                                          #Prend la valeur des jours
    if date[1] == "01": new_date += " Jan"
    elif date[1] == "02": new_date += " Fev"
    elif date[1] == "03": new_date += " Mar"
    elif date[1] == "04": new_date += " Avr"
    elif date[1] == "05": new_date += " Mai"                                    #En fonction de la valeur de MM (nombre),on rajoute la valeur MMM (lettres) correspondante
    elif date[1] == "06": new_date += " Juin"
    elif date[1] == "07": new_date += " Juill"
    elif date[1] == "08": new_date += " Aou"
    elif date[1] == "09": new_date += " Sep"
    elif date[1] == "10": new_date += " Oct"
    elif date[1] == "11": new_date += " Nov"
    else: new_date += " Dec"
    return new_date

#Sert à la projection des courbes
def projectionObjectif(fonction):
    projection = list(fonction)
    coeff =  (fonction[-1]-fonction[-8])/7                                      #Évolution de la courbe calculé à partir des 7 derniers jours
    while len(liste_dates) != len(projection):
        projection.append(projection[-1]+coeff)
    return projection

#Sert à espacer les dates selon limite_ecart_jour
def ecartDate(liste):
    if limite_ecart_jour == 0: return liste
    new_liste = []
    for i in range(len(liste)):
        if i % limite_ecart_jour == 0: new_liste.append(liste[i])
    return new_liste

fichier = open(nom_fichier,"r")                                                 #Ouvre le fichier
ligne_descripteurs = fichier.readline()
lst_descripteurs = ligne_descripteurs.rstrip().rsplit(";")                      #Sépare la première ligne (titres des colonnes) du reste des valeurs numériques
lignes = fichier.readlines()                                                    #Le reste est entreposée dans "lignes"
table = []

if limite_date_debut == 0: suppressionDate = False
else: suppressionDate = True

for ligne in lignes:
    lst = ligne.rstrip().split(";")
    del lst[0]                                                                  #Supression des valeurs du pays de l'injection (toutes dans le fichier sont en France)
    lst[0] = int(lst[0])                                                        #Conversion de l'âge des vaccinés en nombre entier (de base une chaine de caractères.)
    del lst[2]                                                                  #Suppression des primo-injections quotidiennes
    del lst[2]                                                                  #Suppression des injections complètes quotidiennes
    lst[2] = int(lst[2])                                                        #Conversion du cumul des primo-injections en nombre entier
    lst[3] = int(lst[3])                                                        #Conversion du cumul des injections complètes en nombre entier
    lst[4] = float(lst[4])                                                      #Conversion du taux de primo-vaccinés en nombre entier
    lst[5] = float(lst[5])                                                      #Conversion du taux de vaccinés en nombre entier
    table.append(lst)
fichier.close()                                                                 #Ferme le fichier
table = sorted(table, key=itemgetter(1, 0))                                     #Tri les données par date, puis par âge

while suppressionDate and table[0][1] != limite_date_debut: del table[0]        #Tant que la date limite n'est pas atteinte, continuer de supprimer les données

#Initialisation des variables des dates et des 7 autres courbes
liste_dates = []

primo_injections_18_ans = []
primo_injections_50_ans = []
primo_injections_totales = []
injections_completes_18_ans = []
injections_completes_totales = []
proportion_primo_vaccines = []
proportion_vaccines = []
    
cumul_primo_injections_18_ans = 0
cumul_injections_completes_18_ans = 0
cumul_primo_injections_50_ans = 0
    
for donnees in table:
    #Afin de faciliter la compréhension du code, les 4 colonnes sont assignés à des variables
    age = donnees[0]
    date = donnees[1]
    primo_injections = donnees[2]
    injections_completes = donnees[3]
    taux_primo_vaccines = donnees[4]
    taux_vaccines = donnees[5]

    #Dans le cas où la ligne concerne les injections tout âge confondu...
    if age == 0:
        primo_injections_totales.append(primo_injections/obj_1_dose*100)
        injections_completes_totales.append(injections_completes/obj_tot_dose*100)
        liste_dates.append(formatDate(date))
        proportion_primo_vaccines.append(taux_primo_vaccines)
        proportion_vaccines.append(taux_vaccines)

    #Dans le cas où la ligne concerne les injections de personnes entre 18 et 49 ans...
    elif 18 <= age <= 49:
        cumul_primo_injections_18_ans += primo_injections
        cumul_injections_completes_18_ans += injections_completes

    #Dans le cas où la ligne concerne les injections de personnes entre 50 et 79 ans...
    elif 50 <= age <= 79:
        cumul_primo_injections_50_ans += primo_injections
        cumul_primo_injections_18_ans += primo_injections
        cumul_injections_completes_18_ans += injections_completes

    #Dans le cas où la ligne concerne les injections de personnes de plus de 80 ans...
    elif age == 80:
        cumul_primo_injections_50_ans += primo_injections
        primo_injections_50_ans.append(cumul_primo_injections_50_ans/pop_50_ans/obj_50_ans_1_dose*100)
        cumul_primo_injections_50_ans = 0
        
        cumul_primo_injections_18_ans += primo_injections
        cumul_injections_completes_18_ans += injections_completes
        primo_injections_18_ans.append(cumul_primo_injections_18_ans/pop_18_ans/obj_18_ans_1_dose*100)
        injections_completes_18_ans.append(cumul_injections_completes_18_ans/pop_18_ans/obj_18_ans_tot_dose*100)
        cumul_primo_injections_18_ans = 0
        cumul_injections_completes_18_ans = 0

position_date_limite = len(liste_dates)-1                                       #Sauvegarde de la position du dernier jour dont on a les données

#Sert à la création des dates ultérieurs à celles des données
while liste_dates[-1][0:2] != "31" and liste_dates[-1][3:9] == "Juill":
    liste_dates.append(str(int(liste_dates[-1][0:3])+1)+" Juill")
            
if "01 Aou" not in liste_dates: liste_dates.append("01 Aou")
        
while int(liste_dates[-1][0:2]) < 9 and liste_dates[-1][3:6] == "Aou":
    liste_dates.append("0"+str(int(liste_dates[-1][0:2])+1)+" Aou")
        
while liste_dates[-1][0:2] != "31" and liste_dates[-1][3:6] == "Aou":
    liste_dates.append(str(int(liste_dates[-1][0:2])+1)+" Aou")
    
liste_dates_reduite = ecartDate(reduction(liste_dates))                         #Reduit la liste de dates tout en conservant l'original


#Début de la contruction du graphique
plt.figure(figsize=(16,9))                                                      #Définit une dimension en 16/9 à cause de la grande quantité de dates
plt.tick_params(axis = 'x', rotation = 80)                                      #Tourne les dates à 80° afin qu'elles restent visibles
    
plt.axhline(y=100,color='gray',linestyle='--')                                  #Trace une ligne de pointillé verticale au niveau des 100%

#Trace les courbes
plt.plot(liste_dates_reduite, ecartDate(reduction(projectionObjectif(primo_injections_totales))), "red", label = f"Objectif de primo-vaccinés ({int(obj_1_dose/1000000)} M)")
plt.plot(liste_dates_reduite, ecartDate(reduction(projectionObjectif(injections_completes_totales))), "firebrick", label = f"Objectif de vaccinés ({int(obj_tot_dose/1000000)} M)")
plt.plot(liste_dates_reduite, ecartDate(reduction(projectionObjectif(primo_injections_50_ans))), "orange", label = f"Objectif des +50 ans primo-vaccinés ({int(obj_50_ans_1_dose*100)}%)")
plt.plot(liste_dates_reduite, ecartDate(reduction(projectionObjectif(primo_injections_18_ans))), "lawngreen", label = f"Objectif des +18 ans primo-vaccinés ({int(obj_18_ans_1_dose*100)}%)")
plt.plot(liste_dates_reduite, ecartDate(reduction(projectionObjectif(injections_completes_18_ans))), "darkgreen", label = f"Objectif des +18 ans vaccinés ({int(obj_18_ans_tot_dose*100)}%)")
plt.plot(liste_dates_reduite, ecartDate(reduction(projectionObjectif(proportion_primo_vaccines))), "cyan", label = "Référence : Français 100% primo-vaccinés")
plt.plot(liste_dates_reduite, ecartDate(reduction(projectionObjectif(proportion_vaccines))), "darkblue", label = "Référence : Français 100% vaccinés")

#Trace une zone en gris clair entourée de ligne verticales en pointillé pour désigner les prédictions des courbes
plt.axvline(x=liste_dates_reduite[position_date_limite//limite_ecart_jour], color='gray', linestyle='--')
plt.axvspan(liste_dates_reduite[position_date_limite//limite_ecart_jour], liste_dates[-1], alpha=0.5, color='lightgray')
plt.axvline(x=liste_dates[-1], color='gray', linestyle='--')
    
#Limite l'axe y à maximum 105% et force la création de jalons de 10%
plt.yticks(np.arange(0, 110, 10))
plt.ylim(0, 105)

plt.grid()                                                                      #Ajout d'un grillage
plt.legend()                                                                    #Affiche les légendes associés à la courbe correspondante
plt.margins(0, 0)                                                               #Force la disparition des marges intérieures
    
#Défini les titres du graphes et des axes x et y
plt.title(f"État des objectifs gouvernementaux pour la fin Août (Données du {formatDate(nom_fichier[12:22])})")
plt.xlabel("Dates")
plt.ylabel("Pourcentage atteint des objectifs (%)")
    
#Sauvegarde l'image suivant la date des données en 170 pouces de diagonale, et supprime et les marges exterieures
plt.savefig(f"Tableau {date}.png", dpi=170, bbox_inches='tight')
plt.show()
