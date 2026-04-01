import os
import sys
from configparser import ConfigParser
from connect_t_users import *
from connect_t_production import * 
from tkinter import *
from tkinter import messagebox
from customtkinter import *
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))) 
    return os.path.join(base_path, relative_path)

configscanini = resource_path("config\\config_ScanDataM.ini")
config = ConfigParser()
config.read(configscanini)

SERVEUR_DATABASE = config['DATABASE']['SERVER']
DATABASE = config['DATABASE']['DATABASE']
USER_DATABASE = config['DATABASE']['USER']
PASSWORD_DATABASE = config['DATABASE']['PASSWORD']
CARACTERE_MATRICULE_MAX = int(config['PARAMETRES']['CARACTERE_MATRICULE_MAX'])
CARACTERE_CARTE_MAX = int(config['PARAMETRES']['CARACTERE_CARTE_MAX'])
CARACTERE_BATTERIE_MAX = int(config['PARAMETRES']['CARACTERE_BATTERIE_MAX'])
DATAMATRIX_LEFT_MAX = int(config['PARAMETRES']['DATAMATRIX_LEFT_MAX'])
DATAMATRIX_RIGHT_MAX = int(config['PARAMETRES']['DATAMATRIX_RIGHT_MAX'])

nom_trouve_BDD = None
BDD_matricule = None
DateTime_verification = None
prenom = None
nom = None
right = None

nom_trouve = False
boitier_trouve = False
LabelBoitierAffichage = None


id_production = None
lbl_carte = None
lbl_batterie = None
lbl_boitier = None

def MATRICULE_SAISIE(): # Vérification des caractères du matricule 
    global CARACTERE_MATRICULE_MAX, Matricule_saisie
    Matricule = Infos_Matricule.get().strip()
    if Matricule.isnumeric() and len(Matricule) == CARACTERE_MATRICULE_MAX:
        Matricule_saisie.config(fg="green")
    else:
        Matricule_saisie.config(fg="red")

def BATTERIE_saisie() : 
    global CARACTERE_BATTERIE_MAX, DataMatrix_Batterie_Entry
    Batterie_Saisie = DataMatrix_Batterie.get().strip()
    if len(Batterie_Saisie) == CARACTERE_BATTERIE_MAX:
        DataMatrix_Batterie_Entry.config(fg="green")
    else:
        DataMatrix_Batterie_Entry.config(fg="red")
    

def CARTE_Saisie() : 
    global  CARACTERE_CARTE_MAX,DataMatrix_Carte_Entry
    Carte_Saisie = DataMatrix_Carte.get().strip()
    if len(Carte_Saisie) == CARACTERE_CARTE_MAX: 
        DataMatrix_Carte_Entry.config(fg="green")
    else:
        DataMatrix_Carte_Entry.config(fg="red")

def Boitier_Saisie() : 
    global DATAMATRIX_LEFT_MAX, DATAMATRIX_RIGHT_MAX, DataMatrix_Boitier_Entry
    Boitier_saisie = DataMatrix_Boitier.get().strip()
    if len(Boitier_saisie) == DATAMATRIX_LEFT_MAX or len(Boitier_saisie) == DATAMATRIX_RIGHT_MAX : 
        DataMatrix_Boitier_Entry.config(fg="green")
    else : 
        DataMatrix_Boitier_Entry.config(fg="red")


def Afficher_Matricule_Nom(): # Vérification de la présence du matricule dans la BDD
    global nom_trouve_BDD, BDD_matricule, Matricule_trouve, nom_trouve, prenom, nom, right 
    
    Matricule_saisie = Infos_Matricule.get().strip()
    print("Infos Matricule", Matricule_saisie)

    if not row:
        messagebox.showerror("Erreur", "Aucune donnée dans la base de données !")
        return

    Matricule_trouve = False

    for i in row:
        Matricule = str(i[0]).strip()
        if Matricule_saisie == Matricule:
            nom_trouve_BDD = i[1]
            prenom, nom = nom_trouve_BDD.split(" ", 1)
            BDD_matricule = i[0]
            Nom_utilisateur_title.config(text=f"Nom : {nom}")
            Prenom_utilisateur_title.config(text=f"Prénom : {prenom}")
            Matricule_trouve_title.config(text=f"Matricule : {BDD_matricule}") # pour la frame boitier afficher les infos matricule
            
            Nom_utilisateur_title_scan.config(text=f"Nom : {nom}")
            Prenom_utilisateur_title_scan.config(text=f"Prénom : {prenom}")
            Matricule_trouve_title_scan.config(text=f"Matricule : {BDD_matricule}")  # Pour la frame batterie + carte infos matricule


            # Vérification des droits
            Droit_Matricule = int(i[2])
            if Droit_Matricule < 3:
                messagebox.showerror("Matricule", 
                )
                         
                return
            messagebox.showinfo("Matricule", f"Matricule : {i[0]} \n Nom : {i[1]}")
            Matricule_trouve = True
            nom_trouve = True
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

    
def Afficher_Frame_Boitier() :
    Afficher_Matricule_Nom()
    if nom_trouve and Matricule_trouve : # Si le nom et le matricule sont trouvés dans la base de données.
        Frame_Scan_Boitier.tkraise() # Afficher la frame pour scanner les balises
        Changer_la_taille_de_la_fenetre_Boitier()
    else:
        messagebox.showerror("Erreur", "Veuillez entrer un matricule valide") 

def Scan_Boitier() :  # Recheche du boîtier dans la base de données 
    global boitier_trouve, id_production, LabelBoitierAffichage, lbl_carte, lbl_batterie, lbl_boitier
    Balise_scannee = DataMatrix_Boitier.get().strip()
    print("Balise scannée :", Balise_scannee)
        
    try : 
        db = mysql.connector.connect(user =USER_DATABASE, password=PASSWORD_DATABASE, host=SERVEUR_DATABASE, database=DATABASE)
        cursor = db.cursor()
        
        cursor.execute("SELECT * FROM t_production WHERE lbl_boitier LIKE %s",('%'+Balise_scannee+'%',))
        lbl_trouve= cursor.fetchall()  # Récupère TOUS les résultats dans la base
        
        # print('label trouve',lbl_trouve)
    except Exception as e:
        print("Erreur lors de la connexion à la base de données : ", e)
        lbl_trouve = []
    print ("lbl_trouve",lbl_trouve)
    for i in lbl_trouve : 
        id_production = i[0]
        print("id", id_production)
        lbl_carte = i[3]
        print("lbl_carte :", lbl_carte)
        lbl_batterie = i[4]
        print("lbl_batterie :", lbl_batterie)
        lbl_boitier = i[5]
        print("lbl_boitier : ", lbl_boitier)
        
    if  lbl_trouve ==[] : 
        messagebox.showerror("Erreur","Le DataMatrix Scanné n'existe pas")
        return 
    if lbl_trouve !=[] : 
        boitier_trouve = True
        messagebox.showinfo("Balise trouvée !",f"Balise présente dans la base id : {id_production}")
          
    
    # LabelBoitierAffichage = lbl_boitier[:12]
    # LabelBoitierAffichage_title.config(text=f"Vous êtes sur la balise : {LabelBoitierAffichage}") # Afficher ke SERIAL NUMBER sur la frame 
    # if not boitier_trouve : 
    #     messagebox.showerror("Erreur", "Le Datamatrix n'est pas dans la base de données" )

def Afficher_frame_scan_batterie_carte(): 
    global id_production, DataMatrix_Boitier_Entry
    Boitier_saisie = DataMatrix_Boitier.get().strip()
    if Boitier_saisie =="" or DataMatrix_Boitier_Entry.cget("fg") == "red":
        messagebox.showerror("Erreur", "Veuillez revérifier le DataMatrix saisie.")
        return
    Scan_Boitier()
    if boitier_trouve and  id_production != None :  #Si le SN boitier est trouver et id n'est pas vide 
        Frame_Scan.tkraise()
        Changer_la_taille_de_la_fenetre()

def Valider_Modification():
    global CARACTERE_BATTERIE_MAX, DataMatrix_Batterie_Entry, CARACTERE_CARTE_MAX,DataMatrix_Carte_Entry
    
    Carte_Saisie = DataMatrix_Carte.get().strip()
    Batterie_Saisie = DataMatrix_Batterie.get().strip()
    
    if Carte_Saisie =="" or DataMatrix_Carte_Entry.cget("fg") == "red":
        messagebox.showerror("Erreur", "Veuillez revérifier le DataMatrix de la carte.")
        return 
    if Batterie_Saisie =="" or DataMatrix_Batterie_Entry.cget("fg") == "red":
        messagebox.showerror("Erreur", "Veuillez revérifier le DataMatrix de la batterie.")
        return 
 



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

Bouton_Valider = Button(Frame_Matricule, text="Valider", command=Afficher_Frame_Boitier, bg="grey") 
Bouton_Valider.place(x=300, y=70)


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
Bouton_Valider = Button(Frame_Scan_Boitier, text="OK", command=Afficher_frame_scan_batterie_carte, bg="grey") 
Bouton_Valider.place(x=450, y=140)

Frame_Scan = Frame(App_Scan)
Frame_Scan.place(x=0, y=0, relwidth=1, relheight=1)
DataMatrix_Carte = StringVar()
DataMatrix_Batterie = StringVar()

Image_Asteelflash = PhotoImage(file=resource_path("Images\\Asteelflash.png"))
Image_Asteelflash_reduite = Image_Asteelflash.subsample(3,3)
Label_Asteelflash_image = Label(Frame_Scan, image=Image_Asteelflash_reduite)
Label_Asteelflash_image.place(x=3, y=2)

Image_Asteelflash_reduite_boitier = Image_Asteelflash.subsample(3,3)
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

CheckBox1 = CTkCheckBox( Frame_Scan, text="Garder le SERIAL NUMBER",font= ("Calibri", 16),text_color="black" )
CheckBox1.place(x=200, y=300)
CheckBox2 = CTkCheckBox( Frame_Scan, text="Changer le SERIAL NUMBER",font= ("Calibri", 16),text_color="black" ) # Afficher les checkbox de choix de option SN
CheckBox2.place(x=500, y=300)
LabelBoitierAffichage_title = Label (Frame_Scan, text=f"Vous êtes sur la balise : {LabelBoitierAffichage}",font= ("Calibri", 18))
LabelBoitierAffichage_title.place(x=200, y=20)
Bouton_validation_final = Button(Frame_Scan, text="Valider", command=Valider_Modification, bg="grey") 
Bouton_validation_final.place(x=900, y=350)

App_Scan.iconbitmap(resource_path('Images\\Asteelflash_icon.ico'))

Frame_Matricule.tkraise()
App_Scan.mainloop()