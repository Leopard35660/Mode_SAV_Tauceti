import os
import shlex
import shutil
import sys
import re
from configparser import ConfigParser
from tkinter import *
from tkinter import messagebox
from customtkinter import *
import datetime as dt
from zebra import Zebra
from connect_t_users import *
from connect_t_production import * 
import subprocess
import csv


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))) 
    return os.path.join(base_path, relative_path)

configscanini = resource_path("config\\config_ScanDataM.ini")
config = ConfigParser(interpolation= None)
config.read(configscanini)

# cf config_ScanDataM.ini
SERVEUR_DATABASE = config['DATABASE']['Server']
DATABASE = config['DATABASE']['Database']
USER_DATABASE = config['DATABASE']['User']
PASSWORD_DATABASE = config['DATABASE']['Password']

CARACTERE_MATRICULE_MAX = int(config['PARAMETRES']['CARACTERE_MATRICULE_MAX'])
CARACTERE_CARTE_MAX = int(config['PARAMETRES']['CARACTERE_CARTE_MAX'])
CARACTERE_BATTERIE_MAX = int(config['PARAMETRES']['CARACTERE_BATTERIE_MAX'])
DATAMATRIX_LEFT_MAX = int(config['PARAMETRES']['DATAMATRIX_LEFT_MAX'])
DATAMATRIX_RIGHT_MAX = int(config['PARAMETRES']['DATAMATRIX_RIGHT_MAX'])

EXPIRATIONBATT = int(config['CONTROL']['ExpirationBatt'])
CDOMBATT = int(config['CONTROL']['CDOMBatt'])

FICHIER_PRN_SKELETON = config['LABEL']['Source'] 
FICHIER_PRN_BALISE = config['LABEL']['Output'] 
 
DATAM_GAUCHE_SKELETON= config['LABEL']['DataMatrixBox'] 
DATAM_DROITE_SKELETON = config['LABEL']['DataMatrixContent'] 
PNR_SKELETON = config['LABEL']['PNR'] # %PNR% 
SER_SKELETON = config['LABEL']['SER'] # %SER%
CSN_SKELETON = config['LABEL']['CSN'] # %CSN%

PRINTERARG = config['LABEL']['PrinterArg'] 
PRINTEREXE = config['LABEL']['PrinterExe'] 

CSV_REPARATION = config['LOGGING']['RepDir'] 

nom_trouve_BDD = None
BDD_matricule = None
id_user = None
prenom = None
nom = None
right = None

nom_trouve = False
boitier_trouve = False
LabelBoitierAffichage = None

id_production = None
matricule_table = None
date_table = None
lbl_carte = None
lbl_batterie = None
lbl_boitier = None
type_produit = None 
status = None

Expiration_Batt = None
Cdom = None

Nouveau_SER = None

pnr_datam = None
ser_datam = None
csn_datam = None

fichier_copie = None
impression_reussi = False

aujourdhui = None
f_case_final = None
f_boxright_final = None
f_boxright = None
def MATRICULE_SAISIE(): # Vérification des caractères du matricule 
    global CARACTERE_MATRICULE_MAX, Matricule_saisie
    Matricule = Infos_Matricule.get().strip()
    if Matricule.isnumeric() and len(Matricule) == CARACTERE_MATRICULE_MAX:
        Matricule_saisie.config(fg="green")
    else:
        Matricule_saisie.config(fg="red")

def BATTERIE_saisie() : # Verification de la longueur de la chaîne saisie pour la batterie
    global CARACTERE_BATTERIE_MAX, DataMatrix_Batterie_Entry
    Batterie_Saisie = DataMatrix_Batterie.get().strip()
    if len(Batterie_Saisie) == CARACTERE_BATTERIE_MAX:
        DataMatrix_Batterie_Entry.config(fg="green")
    else:
        DataMatrix_Batterie_Entry.config(fg="red")

def CARTE_Saisie() : # Verification de la longueur de la chaîne saisie pour la carte
    global  CARACTERE_CARTE_MAX,DataMatrix_Carte_Entry
    Carte_Saisie = DataMatrix_Carte.get().strip()
    if len(Carte_Saisie) == CARACTERE_CARTE_MAX: 
        DataMatrix_Carte_Entry.config(fg="green")
    else:
        DataMatrix_Carte_Entry.config(fg="red")

def Boitier_Saisie() : # Verification de la longueur de la chaîne saisie pour le boitier
    global DATAMATRIX_LEFT_MAX, DATAMATRIX_RIGHT_MAX, DataMatrix_Boitier_Entry
    Boitier_saisie = DataMatrix_Boitier.get().strip()
    if len(Boitier_saisie) == DATAMATRIX_LEFT_MAX or len(Boitier_saisie) == DATAMATRIX_RIGHT_MAX : 
        DataMatrix_Boitier_Entry.config(fg="green")
    else : 
        DataMatrix_Boitier_Entry.config(fg="red")

def Afficher_Matricule_Nom(): # Vérification de la présence du matricule dans la BDD
    global nom_trouve_BDD, BDD_matricule, Matricule_trouve, nom_trouve, prenom, nom, right, id_user
    
    Matricule_saisie = Infos_Matricule.get().strip()
    print("Infos Matricule", Matricule_saisie)
    if not row: # Si la ligne du matricule n'est pas trouvée
        messagebox.showerror("Erreur", "Aucune donnée dans la base de données !")
        return
    Matricule_trouve = False

    for i in row: # Pour chaque donnée trouvée dans la base table t_users cf connect_t_users.py
        Matricule = str(i[1]).strip()

        if Matricule_saisie == Matricule:
            id_user = i[0] # 1ère colonne de la table
            nom_trouve_BDD = i[2]
            print("nom trouvé",nom_trouve_BDD)
            prenom, nom = nom_trouve_BDD.split(" ", 1) # Séparer l'espace pour le nom et prénom 
            BDD_matricule = i[1]
            Nom_utilisateur_title.config(text=f"Nom : {nom}")
            Prenom_utilisateur_title.config(text=f"Prénom : {prenom}")
            Matricule_trouve_title.config(text=f"Matricule : {BDD_matricule}") # pour la frame boitier afficher les infos matricule
            
            Nom_utilisateur_title_scan.config(text=f"Nom : {nom}")
            Prenom_utilisateur_title_scan.config(text=f"Prénom : {prenom}")
            Matricule_trouve_title_scan.config(text=f"Matricule : {BDD_matricule}")  # Pour la frame batterie + carte infos matriculeAA2125265913;   09/2025 477685 02/2033;B ;S1863521-03B   ; 

            # Vérification des droits
            Droit_Matricule = int(i[3])
            if Droit_Matricule < 3: # Si le droit est inferieur à 3 : Stopper l'applicatif
                messagebox.showerror("Matricule", "Vous n'avez pas les droits pour continuer")
                return
            else: # Sinon afficher le matricule et le nom
                messagebox.showinfo("Matricule", f"Matricule : {i[1]} \n Nom : {i[2]}")
                Matricule_trouve = True
                nom_trouve = True
                Frame_Matricule.place_forget()
                break

    if not Matricule_trouve:
        messagebox.showerror("Erreur de saisie", "Matricule non trouvé dans la base de données.")
        return

def Changer_la_taille_de_la_fenetre_Boitier(): # Fonction pour changer la taille de la fenêtre pour scanner le boîtier
    App_Scan.geometry("600x350")
    largeur_ecran = App_Scan.winfo_screenwidth()
    longueur_ecran = App_Scan.winfo_screenheight()
    largeur=500
    longueur=200
    x = (largeur_ecran/2) - (largeur/2)
    y = (longueur_ecran/2) - (longueur/2)
    App_Scan.geometry('%dx%d+%d+%d' % (largeur, longueur, x, y))

def Changer_la_taille_de_la_fenetre(): # Fonction pour changer la taille de la fenêtre pour scanner les balises
    App_Scan.geometry("1000x400")
    largeur_ecran = App_Scan.winfo_screenwidth()
    longueur_ecran = App_Scan.winfo_screenheight()
    largeur=1000
    longueur=400
    x = (largeur_ecran/2) - (largeur/2)
    y = (longueur_ecran/2) - (longueur/2)
    App_Scan.geometry('%dx%d+%d+%d' % (largeur, longueur, x, y))

def Afficher_Frame_Boitier() : # Afficher la frame boitier 
    Afficher_Matricule_Nom()
    if nom_trouve and Matricule_trouve : # Si le nom et le matricule sont trouvés dans la base de données.
        Frame_Scan_Boitier.tkraise() # Afficher la frame pour scanner les balises
        Changer_la_taille_de_la_fenetre_Boitier()
        DataMatrix_Boitier_Entry.focus()
    else:
        messagebox.showerror("Erreur", "Veuillez entrer un matricule valide") 
def Afficher_Frame_Scan():
    Frame_Matricule.place_forget()
    Frame_Scan_Boitier.place_forget()
    Frame_Scan.place(x=0, y=0, relwidth=1, relheight=1)
    Frame_Scan.tkraise()
    Changer_la_taille_de_la_fenetre()
    DataMatrix_Batterie_Entry.delete(0,END)
    DataMatrix_Carte_Entry.delete(0,END)
    DataMatrix_Carte_Entry.focus()
def Scan_Boitier() :  # Recheche du boîtier dans la base de données 
    global boitier_trouve, id_production, LabelBoitierAffichage, lbl_carte, lbl_batterie, lbl_boitier, matricule_table,date_table, type_produit, status
    boitier_trouve = False
    id_production = None
    Balise_scannee = DataMatrix_Boitier.get().strip()
    print("Balise scannée :", Balise_scannee)
        
    try : # Connexion à la base de données
        db = mysql.connector.connect(user =USER_DATABASE, password=PASSWORD_DATABASE, host=SERVEUR_DATABASE, database=DATABASE)
        cursor = db.cursor()
        # Trouver la ligne contenant la ligne de la balise comme commande SQL LIKE%%
        cursor.execute("SELECT * FROM t_production WHERE lbl_boitier LIKE '%" + Balise_scannee + "%'")
        lbl_trouve= cursor.fetchall()  # Récupère TOUS les résultats dans la base
    
    except Exception as e:
        print("Erreur lors de la connexion à la base de données : ", e)
        lbl_trouve = []
    print ("lbl_trouve",lbl_trouve)
    for i in lbl_trouve : 
        # Séparer toutes les infos trouvés 
        id_production = i[0]
        print("id", id_production)
        matricule_table = i[1]
        print("matricule :", matricule_table)
        date_table = i[2]
        print("date :", date_table)
        lbl_carte = i[3]
        print("lbl_carte :", lbl_carte)
        lbl_batterie = i[4]
        print("lbl_batterie :", lbl_batterie)
        lbl_boitier = i[5]
        print("lbl_boitier : ", lbl_boitier)
        type_produit = i[6]
        print("type produit :", type_produit)
        status = i[7]
        print("statuts :", status)
    if  lbl_trouve ==[] : 
        messagebox.showerror("Erreur","Le DataMatrix Scanné n'existe pas")
        return 
    if lbl_trouve !=[] : 
        boitier_trouve = True
        messagebox.showinfo("Balise trouvée !",f"Balise présente dans la base id : {id_production}")
          
    LabelBoitierAffichage = lbl_boitier[:12]
    LabelBoitierAffichage_title.config(text=f"Vous êtes sur la balise : {LabelBoitierAffichage}") # Afficher le SERIAL NUMBER sur la frame scanner carte batterie
    
def Afficher_frame_scan_batterie_carte(): #Afficher la frame carte batterie 
    global id_production, DataMatrix_Boitier_Entry
    Boitier_saisie = DataMatrix_Boitier.get().strip()
    if Boitier_saisie =="" or DataMatrix_Boitier_Entry.cget("fg") == "red":
        messagebox.showerror("Erreur", "Veuillez revérifier le DataMatrix saisie.")
        return
    Scan_Boitier()
    if boitier_trouve and  id_production != None :  #Si le SN boitier est trouver et id n'est pas vide 
        Afficher_Frame_Scan()
        

def Verif_Infos_Batt(): # Vérifier si la batterie n'est pas périmée 
    global  EXPIRATIONBATT,CDOMBATT, lbl_batterie
    global Expiration_Batt, Cdom
    Expiration_now =  dt.datetime.today()
    Batterie_Saisie = DataMatrix_Batterie.get().strip()
    Expiration_String =  Batterie_Saisie[31:38]  # Information concernant l'expiration de la batterie 
    Expiration_Batt = dt.datetime.strptime(Expiration_String, "%m/%Y")
    print("Expiration de la batterie :", Expiration_Batt)
    Expiration_restante = (Expiration_Batt.year - Expiration_now.year) * 12 + (Expiration_Batt.month - Expiration_now.month) # Différence en mois

    if Expiration_restante <= EXPIRATIONBATT : # Si la batterie est périmée
        messagebox.showwarning("Batterie expirée", f"La batterie est expirée {Expiration_restante} mois au lieu de {EXPIRATIONBATT} mois")
        return
    
    print("Temps restant EXP : ", Expiration_restante) 
    Cdom_now =  dt.datetime.today()
    Cdom_string = Batterie_Saisie[24:29] # Information concernant le CDOM (Cell Date Of Manufacturing) 
    Cdom = dt.datetime.strptime(Cdom_string, "%m/%y")
    Cdom_duree = (Cdom_now.year -Cdom.year )*12 + (Cdom_now.month - Cdom.month) # Différence en mois
    print("Temps restant DOM : ", Cdom_duree)
    
    if Cdom_duree >= CDOMBATT : # Si le CDOM calculé est superieur au tolérence 
        messagebox.showwarning("CDOM périmé", f"Le CDOM est périmé {Cdom_duree} mois au lieu de {CDOMBATT} mois")
        return                                  

def Generer_Etiquette(): # Génerer les nouvelles informations de l'etiquette
    global Nouveau_SER, id_production
    changer_etiquette = result_checkbox2.get() #Récuperer le choix de l'utilisateur concernant le changement de SN
    print("resultat checkbox : ", changer_etiquette)
    Annee = dt.date.today()
    Annee_2digits = Annee.strftime("%y")
    print(Annee_2digits)
    jourdelan = Annee.strftime("%j")
    id_3digits = str(id_production)[-3:]
    print("id :", id_3digits)

    if changer_etiquette == 1 : # Si le choix est le changement de SN 
        Nouveau_SER = f"AA21{Annee_2digits}{jourdelan}{id_3digits}" # Genérer le nouveau dataMatrix
        print("Nouveau_SER :", Nouveau_SER)
        Nouveau_SER = str(Nouveau_SER)

def Composition_DataMatrix_Gauche(): # Génerer le DataMatrix de gauche 
    global Nouveau_SER, lbl_boitier, f_case, f_case_final
    changer_SN= result_checkbox2.get()
    Batterie_Saisie = DataMatrix_Batterie.get().strip()
    print(f_case)# f_case et f_boxright sont des variables récuperer dans la table t_product cf connect_t_products.py
    if f_case is None: 
        print("Aucun résultat SQL")
        return
    # Transformer f_case en string pour le modifier 
    f_case_final= str(f_case[0]) 
    Nouveau_SER = str(Nouveau_SER)
    Old_SER = lbl_boitier[:12]
    Annee = dt.date.today()
    mois = Annee.strftime("%m")
    an = Annee.strftime("%Y")
    csn = lbl_boitier[24:30]
    ed = Batterie_Saisie[31:38]
    # f_case est récupérer sous format brut 
    # Enlever les caractères indésirable hors resultat souhaité              
    f_case_final = f_case_final.replace("(", "") 
    f_case_final = f_case_final.replace(")", "")
    f_case_final = f_case_final.replace(",", "")
    f_case_final = f_case_final.replace("'", "")
    print(f_case)
    print(f_case_final)
    # Dans le cas où on change le SN
    if changer_SN == 1 :
        # Remplacer le squelette de f_case par les informations de la balise
        f_case_final = f_case_final.replace("AA21%YY%%DDD%%NNN%",Nouveau_SER)  
        f_case_final = f_case_final.replace("%MM%", mois)
        f_case_final = f_case_final.replace("%YYYY%", an)
        f_case_final = f_case_final.replace("%CSN%", csn)
        f_case_final = f_case_final.replace("%ED%", ed)
        print("New DataM Gauche :",f_case_final)
    else : 
        f_case_final = f_case_final.replace("AA21%YY%%DDD%%NNN%",Old_SER)
        f_case_final = f_case_final.replace("%MM%", mois)
        f_case_final = f_case_final.replace("%YYYY%", an)
        f_case_final = f_case_final.replace("%CSN%", csn)
        f_case_final = f_case_final.replace("%ED%", ed) 
        print("OLD DataM Gauche :",f_case)

def Composition_DataMatrix_Droite(): # Générer le DataMatrix de droite 
    global lbl_batterie,lbl_carte,f_boxright, f_boxright_final
    Batterie_Saisie = DataMatrix_Batterie.get().strip()
    Carte_Saisie = DataMatrix_Carte.get().strip()
    # Définir des variables de f_boxright
    psn = Carte_Saisie.split(";")[0]
    ppn = Carte_Saisie.split(";")[3][:14]
    psw = Carte_Saisie.split(";")[1][11:21]
    bsn = Batterie_Saisie.split(";")[0]
    bpn = Batterie_Saisie.split(";")[3][0:14]
    exp = Batterie_Saisie[31:38]
    dom = Batterie_Saisie[16:23]
    # Formater la date cdom en MM/YYYY
    cdom = dt.datetime.strptime("01/" + Batterie_Saisie.split(";")[1][11:16], "%d/%m/%y").strftime("%m/%Y")
    if f_boxright is None:
        print("Aucun résultat SQL")
        return
    f_boxright_final = str(f_boxright[0])
    f_boxright_final = f_boxright_final.replace("(", "") 
    f_boxright_final = f_boxright_final.replace(")", "")
    f_boxright_final = f_boxright_final.replace(",", "") 
    f_boxright_final = f_boxright_final.replace("'", "")
    # Remplacer le squelette de f_boxright par les informations de la balise
    f_boxright_final = f_boxright_final.replace("%PSN%", psn)
    f_boxright_final = f_boxright_final.replace("%PPN%", ppn)
    f_boxright_final = f_boxright_final.replace("%PSW%", psw)
    f_boxright_final = f_boxright_final.replace("%BSN%", bsn)
    f_boxright_final = f_boxright_final.replace("%BPN%", bpn)
    f_boxright_final = f_boxright_final.replace("%CDOM%", cdom)
    f_boxright_final = f_boxright_final.replace("%DOM%", dom)
    f_boxright_final = f_boxright_final.replace("%EXP%", exp)
    print("DataMDroite",f_boxright_final)
    
def Recherche_Infos_DataMatrix(): # Recherche des infos importantes dans le DataMatrix de gauche 
    global pnr_datam, ser_datam, csn_datam, f_case
       
    csn_datam = f_case_final[24:30]
    print("CSN :", csn_datam)
    ser_datam = f_case_final[:12]
    print("SER :", ser_datam)
    pnr_datam = f_case_final[42:53]
    print("PNR :", pnr_datam)

def Recherche_Infos_SKELETON(): # Modifier le fichier prn à partir du skeleton 
    global id_production, fichier_copie, f_case_final, f_boxright_final
    global pnr_skeleton, pnr_datam, ser_skeleton, ser_datam, CSN_skeleton, csn_datam, datamdroite_skeleton,datamgauche_skeleton
    print("DEBUG f_boxright_final :", f_boxright_final)
    date = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    nom_fichier_Sauvegarder = f"Tauceti_{id_production}_{date}.prn" # Nom du fichier à sauvegarder 
    fichiersauvegarder = os.path.join(FICHIER_PRN_BALISE, nom_fichier_Sauvegarder)
    fichier_copie = shutil.copyfile(FICHIER_PRN_SKELETON, fichiersauvegarder) # Copier le SKELETON sous un nouveau nom
    with open(fichier_copie, "r") as fichier:
        contenu = fichier.read()
    nouveau_contenu = contenu
    
    # PNR 
    for ligne in contenu.splitlines():
        if PNR_SKELETON in ligne: # Remplacer dans le skeleton le %PNR% par le PNR de la balise
            pnr_skeleton = re.search(r"\^FD(.+?)\^FS", ligne).group(1)
            print("PNR :", pnr_skeleton)
            nouveau_contenu = nouveau_contenu.replace(pnr_skeleton, pnr_datam)
            break

    # SER 
    for ligne in contenu.splitlines():
        if SER_SKELETON in ligne:
            ser_skeleton = re.search(r"\^FD(.+?)\^FS", ligne).group(1)
            print("SER :", ser_skeleton)
            nouveau_contenu = nouveau_contenu.replace(ser_skeleton, ser_datam)
            break

    # CSN 
    for ligne in contenu.splitlines():
        if CSN_SKELETON in ligne:
            CSN_skeleton = re.search(r"\^FD(.+?)\^FS", ligne).group(1)
            print("CSN :", CSN_skeleton)
            nouveau_contenu = nouveau_contenu.replace(CSN_skeleton, csn_datam)
            break

    # DATAMATRIX GAUCHE 
    for ligne in contenu.splitlines():
        if DATAM_GAUCHE_SKELETON in ligne:
            datamgauche_skeleton = re.search(r"\^FD(.+?)\^FS", ligne).group(1)
            nouveau_contenu = nouveau_contenu.replace(datamgauche_skeleton, f_case_final)
            break


    # DATAMATRIX DROITE 
    for ligne in contenu.splitlines():
        if DATAM_DROITE_SKELETON in ligne:
            datamdroite_skeleton = re.search(r"\^FD(.+?)\^FS", ligne).group(1)
            nouveau_contenu = nouveau_contenu.replace(datamdroite_skeleton, f_boxright_final)
            break
    
    with open(fichier_copie, "w") as fichier:
        fichier.write(nouveau_contenu)
    print("nouveau :", fichier_copie)
    # Ecrire le contenu dans le fichier 
    


def Impression(): # Imprimer l'étiquette 
    global fichier_copie, impression_reussi, f_case_final
    try : 
        # Remplacement du placeholder
        printerArgFinal = PRINTERARG.replace("%LBL%", fichier_copie)
        # Découpage des arguments car il y'a 2 commandes à envoyer 
        args = shlex.split(printerArgFinal)
        print_process = subprocess.Popen([PRINTEREXE] + args,shell=False)
        print_process.wait()
        impression_reussi = True
    except Exception as e :
        print("Erreur d'impression : ", e)
        messagebox.showerror("Problème d'impression")
    if impression_reussi == True : 
        messagebox.showinfo("impression_reussi", "Balise sauvegardée")
        try : 
            db = mysql.connector.connect(user =USER_DATABASE, password=PASSWORD_DATABASE, host=SERVEUR_DATABASE, database=DATABASE)
            cursor = db.cursor()
            # Inserer une nouvelle ligne dans la table t_print 
            cursor.execute("INSERT INTO t_print (lblboitier, mode) VALUES ('" + str(f_case_final) + "', 'REPARATION')")
            db.commit()
            print("Carte saisie différente de lbl-carte")
            print('Les commandes sont faites')         
        except Exception as e:
            print("Erreur lors de la connexion à la base de données : ", e)
    else :  
        messagebox.showinfo("Problème d'impression ", "Appelez le resposable de la ligne")
        return 

def EcrituredansCSV():
    global id_user, id_production, aujourdhui
    global lbl_carte, lbl_batterie, lbl_boitier, csn_datam
    global type_produit, impression_reussi
    aujourdhui = aujourdhui.replace("-", "/") #pour que la date soit sous format YYYY/MM/DD
    type_produit = int(type_produit) # Pour eviter de le mettre entre guillemet dans le csv
    with open(CSV_REPARATION, "a", newline="", encoding="utf-8") as fichier:
        writer = csv.writer(fichier, delimiter=";", quotechar='"', quoting=csv.QUOTE_NONNUMERIC) # QUOTE_NONNUMERIC permet de mettre entre guillemet la date dans le csv
        writer.writerow([id_production, id_user, aujourdhui,
                         lbl_carte, lbl_batterie, lbl_boitier,
                         "", type_produit, 1])
        
def Reset(): 
    global boitier_trouve, id_production, LabelBoitierAffichage, lbl_carte, lbl_boitier, lbl_batterie, date_table, type_produit, status, matricule_table
    Frame_Scan.place_forget()
    Changer_la_taille_de_la_fenetre_Boitier()
    Frame_Scan_Boitier.place(x=0, y=0, relwidth=1, relheight=1)
    boitier_trouve = False 
    id_production = None
    LabelBoitierAffichage = None
    lbl_batterie = None
    lbl_boitier = None
    lbl_carte = None
    date_table = None
    type_produit = None
    status = None 
    matricule_table = None 
    DataMatrix_Boitier_Entry.delete(0,END)
    DataMatrix_Boitier_Entry.focus()

def Valider_Modification(): # Fonction génrérale qui regroupe toutes les actions à réaliser pour valider la balise 

    global CARACTERE_BATTERIE_MAX, DataMatrix_Batterie_Entry, CARACTERE_CARTE_MAX,DataMatrix_Carte_Entry,f_case, f_boxright
    global lbl_carte,lbl_boitier,lbl_batterie,id_production, date_table,matricule_table, type_produit, status, id_user, aujourdhui
    try : 
        db = mysql.connector.connect(user =USER_DATABASE, password=PASSWORD_DATABASE, host=SERVEUR_DATABASE, database=DATABASE)
        cursor = db.cursor()
        # Selectionner f_case dans la table 
        cursor.execute("SELECT f_case FROM t_products") 
        f_case = cursor.fetchall()  # Récupère TOUS les résultats dans la base
        print(f_case)
        cursor2 = db.cursor()
        cursor2.execute("SELECT f_boxright FROM t_products")
        f_boxright = cursor2.fetchall()
        print(f_case)
        # f_boxright et f_case sont des listes de toutes les valeurs 
        # elles sont appélées dans le sript Scan_DataMatrix.py
    except Exception as e:
        print("Erreur lors de la connexion à la base de données : ", e)
        f_case = []
        f_boxright = []
    
    Verif_Infos_Batt()
    aujourdhui= dt.datetime.today().strftime('%Y-%m-%d %H:%M:%S') 
    Carte_Saisie = DataMatrix_Carte.get().strip()
    Batterie_Saisie = DataMatrix_Batterie.get().strip()
   
    if Carte_Saisie =="" or DataMatrix_Carte_Entry.cget("fg") == "red":
        messagebox.showerror("Erreur", "Veuillez revérifier le DataMatrix de la carte.")
        return 
    if Batterie_Saisie =="" or DataMatrix_Batterie_Entry.cget("fg") == "red":
        messagebox.showerror("Erreur", "Veuillez revérifier le DataMatrix de la batterie.")
        return 
    Generer_Etiquette()
    Composition_DataMatrix_Gauche()
    Composition_DataMatrix_Droite()
    if Carte_Saisie != lbl_carte and Batterie_Saisie != lbl_batterie :  # Si la carte et la batterie ont été changées  
        try : 
            db = mysql.connector.connect(user =USER_DATABASE, password=PASSWORD_DATABASE, host=SERVEUR_DATABASE, database=DATABASE)
            insert = db.cursor()
            insert.execute("INSERT INTO t_repair (id_production, matricule, date, lbl_carte, lbl_batterie, lbl_boitier, type_produit) ""VALUES ('" + str(id_production) + "', '" + str(id_user) + "', '" + str(date_table) + "', '" +str(lbl_carte) + "', '" + str(lbl_batterie) + "', '" + str(lbl_boitier) + "', '" + str(type_produit) + "')")
            update = db.cursor()
            update.execute("UPDATE t_production SET date = '" + str(aujourdhui) + "',lbl_carte = '" + str(Carte_Saisie) + "' ,lbl_batterie = '" + str(Batterie_Saisie) + "' WHERE id_production = '" + str(id_production) + "'")
            db.commit()
            print("batterie et carte saisie saisie différente de lbl carte et batterie ")
            print('Les commandes sont faites')
            Carte_Saisie = lbl_carte
            Batterie_Saisie = lbl_batterie
        except Exception as e:
                print("Erreur lors de la connexion à la base de données : ", e)

    
    elif Carte_Saisie != lbl_carte : # Si la carte est changée
        try : 
            db = mysql.connector.connect(user =USER_DATABASE, password=PASSWORD_DATABASE, host=SERVEUR_DATABASE, database=DATABASE)
            cursor = db.cursor()
            cursor.execute("INSERT INTO t_repair (id_production, matricule, date, lbl_carte, lbl_batterie, lbl_boitier, type_produit) ""VALUES ('" + str(id_production) + "', '" + str(id_user) + "', '" + str(date_table) + "', '" +str(lbl_carte) + "', '" + str(lbl_batterie) + "', '" + str(lbl_boitier) + "', '" + str(type_produit) + "')")
            update = db.cursor()
            update.execute("UPDATE t_production SET date = '" + str(aujourdhui) + "' ,lbl_carte = '" + str(Carte_Saisie) + "' WHERE id_production = '" + str(id_production) + "'")
            db.commit()
            print("Carte saisie différente de lbl-carte")
            print('Les commandes sont faites')
            Carte_Saisie = lbl_carte
        except Exception as e:
            print("Erreur lors de la connexion à la base de données : ", e)

    elif Batterie_Saisie != lbl_batterie : # Si la batterie est changée 
        try : 
            db = mysql.connector.connect(user =USER_DATABASE, password=PASSWORD_DATABASE, host=SERVEUR_DATABASE, database=DATABASE)
            cursor = db.cursor()
            cursor.execute("INSERT INTO t_repair (id_production, matricule, date, lbl_carte, lbl_batterie, lbl_boitier, type_produit) ""VALUES ('" + str(id_production) + "', '" + str(id_user) + "', '" + str(date_table) + "', '" +str(lbl_carte) + "', '" + str(lbl_batterie) + "', '" + str(lbl_boitier) + "', '" + str(type_produit) + "')")
            update = db.cursor()
            update.execute("UPDATE t_production SET date = '" + str(aujourdhui) + "' ,lbl_batterie = '" + str(Batterie_Saisie) + "' WHERE id_production = '" + str(id_production) + "'")
            db.commit()
            print("batterie saisie différente de lbl-batterie")
            print('Les commandes sont faites')
            Batterie_Saisie = lbl_batterie
        except Exception as e:
            print("Erreur lors de la connexion à la base de données : ", e)
            


    elif Carte_Saisie == lbl_carte and Batterie_Saisie == lbl_batterie : # Si aucun changement 
        try : 
            db = mysql.connector.connect(user =USER_DATABASE, password=PASSWORD_DATABASE, host=SERVEUR_DATABASE, database=DATABASE)
            insert = db.cursor()
            insert.execute("INSERT INTO t_repair (id_production, matricule, date, lbl_carte, lbl_batterie, lbl_boitier, type_produit) ""VALUES ('" + str(id_production) + "', '" + str(id_user) + "', '" + str(date_table) + "', '" +str(lbl_carte) + "', '" + str(lbl_batterie) + "', '" + str(lbl_boitier) + "', '" + str(type_produit) + "')")
            update = db.cursor()
            update.execute("UPDATE t_production SET date = '" + str(aujourdhui) + "'WHERE id_production ='" + str(id_production) + "' ")
            db.commit()
            print("batterie saisie et carte saisie identique aux labels BDD")
            print('Les commandes sont faites')
        except Exception as e:
            print("Erreur lors de la connexion à la base de données : ", e)
    Recherche_Infos_DataMatrix()
    Recherche_Infos_SKELETON()
    Impression()
    EcrituredansCSV()
    Reset()


App_Scan = Tk()
App_Scan.iconbitmap(resource_path('Images\\Asteelflash_icon.ico')) #Ajouter l'icône de l'application
App_Scan.title("SAV ULTIMA") # Titre de l'application
App_Scan.geometry("400x100") # Taille initiale de la fenêtre poue la saisie du matricule

Frame_Matricule = Frame(App_Scan)
Frame_Matricule.place(x=0, y=0, relwidth=1, relheight=1)
Infos_Matricule = StringVar()

Matricule_title = Label(Frame_Matricule, text="Entrez votre matricule :", font=("Arial", 10)) 
Matricule_title.place(x=10, y=30)
Matricule_saisie = Entry(Frame_Matricule, textvariable=Infos_Matricule, font=("Calibri", 12), width=20)
Matricule_saisie.place(x=150, y=30)
Matricule_saisie.bind("<KeyRelease>", lambda e: MATRICULE_SAISIE())
Matricule_saisie.focus()



Bouton_Valider = Button(Frame_Matricule, text="Valider", command=Afficher_Frame_Boitier, bg="#005DAB",font=("Arial", 12,"bold"), fg="white") 
Bouton_Valider.place(x=300, y=65)


# Centrer la fenêtre 
largeur_ecran = App_Scan.winfo_screenwidth()
longueur_ecran = App_Scan.winfo_screenheight()
largeur=400
longueur=100
x = (largeur_ecran/2) - (largeur/2)
y = (longueur_ecran/2) - (longueur/2)
App_Scan.geometry('%dx%d+%d+%d' % (largeur, longueur, x, y))

Frame_Scan_Boitier = Frame(App_Scan)
Frame_Scan_Boitier.place(x=0, y=0, relwidth=1, relheight=1)
DataMatrix_Boitier= StringVar()

Nom_utilisateur_title = Label (Frame_Scan_Boitier, text=f"Nom : {nom}",font= ("Calibri", 10))
Nom_utilisateur_title.place(x=400, y=10)
Prenom_utilisateur_title = Label(Frame_Scan_Boitier, text=f"Prenom : {prenom}", font=("Calibri", 10)) 
Prenom_utilisateur_title.place(x=382, y=30)
Matricule_trouve_title = Label (Frame_Scan_Boitier, text=f"Matricule : {BDD_matricule}",font= ("Calibri", 10))
Matricule_trouve_title.place(x=370, y=50)

DataMatrix_Boitier_label = Label(Frame_Scan_Boitier, text= "Scannez le DataMatrix du boîtier : " )
DataMatrix_Boitier_label.place(x=10, y=80)
DataMatrix_Boitier_Entry = Entry(Frame_Scan_Boitier, textvariable=DataMatrix_Boitier, font=("Calibri", 12), width=58)
DataMatrix_Boitier_Entry.place(x=10, y=110)
DataMatrix_Boitier_Entry.bind("<KeyRelease>", lambda e:Boitier_Saisie())

Bouton_Valider = Button(Frame_Scan_Boitier, text="OK", command=Afficher_frame_scan_batterie_carte, bg="#005DAB",font=("Arial", 12,"bold"), fg="white") 
Bouton_Valider.place(x=450, y=160)

Frame_Scan = Frame(App_Scan)
Frame_Scan.place(x=0, y=0, relwidth=1, relheight=1)
DataMatrix_Carte = StringVar()
DataMatrix_Batterie = StringVar()

Image_Asteelflash = PhotoImage(file=resource_path("Images\\Asteelflash.png"))
Image_Asteelflash_reduite = Image_Asteelflash.subsample(3,3)
Label_Asteelflash_image = Label(Frame_Scan, image=Image_Asteelflash_reduite)
Label_Asteelflash_image.place(x=3, y=2)

Image_Asteelflash_reduite_boitier = Image_Asteelflash.subsample(1,1)
Label_Asteelflash_image_boitier = Label(Frame_Scan_Boitier, image=Image_Asteelflash_reduite)
Label_Asteelflash_image_boitier.place(x=3, y=2)

DataMatrix_Carte_title = Label (Frame_Scan, text="CARTE :",font=("Arial", 24))
DataMatrix_Carte_title.place(x=55, y= 100)
DataMatrix_Carte_Entry = Entry (Frame_Scan, textvariable= DataMatrix_Carte, font=("Calibri", 24), width=48)
DataMatrix_Carte_Entry.place(x= 200, y=95)
DataMatrix_Carte_Entry.bind("<KeyRelease>", lambda e: CARTE_Saisie())

DataMatrix_Batterie_title = Label(Frame_Scan, text="BATTERIE :", font=("Arial", 24))
DataMatrix_Batterie_title.place(x=10, y= 200)
DataMatrix_Batterie_Entry = Entry(Frame_Scan, textvariable= DataMatrix_Batterie, font=("Calibri", 24), width=48)
DataMatrix_Batterie_Entry.place(x= 200, y=195)
DataMatrix_Batterie_Entry.bind("<KeyRelease>", lambda e: BATTERIE_saisie())
Nom_utilisateur_title_scan = Label (Frame_Scan, text=f"Nom : {nom}",font= ("Calibri", 10))
Nom_utilisateur_title_scan.place(x=900, y=10)
Prenom_utilisateur_title_scan = Label(Frame_Scan, text=f"Prenom : {prenom}", font=("Calibri", 10)) 
Prenom_utilisateur_title_scan.place(x=882, y=30)
Matricule_trouve_title_scan = Label (Frame_Scan, text=f"Matricule : {BDD_matricule}",font= ("Calibri", 10))
Matricule_trouve_title_scan.place(x=870, y=50)

result_checkbox2= IntVar()

CheckBox2 = CTkCheckBox( Frame_Scan, text="Changer le SERIAL NUMBER", variable= result_checkbox2,font= ("Calibri", 16),text_color="black" ) # Afficher les checkbox de choix de option SN
CheckBox2.place(x=500, y=300)
LabelBoitierAffichage_title = Label (Frame_Scan, text=f"Vous êtes sur la balise : {LabelBoitierAffichage}",font= ("Calibri", 18))
LabelBoitierAffichage_title.place(x=200, y=20)
Bouton_validation_final = Button(Frame_Scan, text="Valider", command=Valider_Modification, bg="#005DAB",font=("Arial", 12,"bold"), fg="white") 

Bouton_validation_final.place(x=900, y=350)

App_Scan.iconbitmap(resource_path('Images\\Asteelflash_icon.ico'))

Frame_Matricule.tkraise()
App_Scan.mainloop()