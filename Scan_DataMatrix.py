import os
import sys
from configparser import ConfigParser
from connexion_Base_Matricule import *
from tkinter import *
from tkinter import messagebox

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))) 
    return os.path.join(base_path, relative_path)

configscanini = resource_path("config\\config_ScanDataM.ini")
config = ConfigParser()
config.read(configscanini)

CARACTERE_MATRICULE_MAX = int(config['PARAMETRES']['CARACTERE_MATRICULE_MAX'])

nom_trouve_BDD = None
BDD_matricule = None
DateTime_verification = None
prenom = None
nom = None
right = None
nom_trouve = False

def MATRICULE_SAISIE():
    global CARACTERE_MATRICULE_MAX, Matricule_saisie
    Matricule = Infos_Matricule.get().strip()
    if Matricule.isnumeric() and len(Matricule) == CARACTERE_MATRICULE_MAX:
        Matricule_saisie.config(fg="green")
    else:
        Matricule_saisie.config(fg="red")

def Afficher_Matricule_Nom():
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
            Matricule_trouve_title.config(text=f"Matricule : {BDD_matricule}")
            # Vérification des droits
            Droit_Matricule = int(i[2])
            if Droit_Matricule < 3:
                messagebox.showerror("Matricule", "Vous n'avez pas les droits pour continuer.")
                Infos_Matricule.delete(END,0)         
                return
            messagebox.showinfo("Matricule", f"Matricule : {i[0]} \n Nom : {i[1]}")
            Matricule_trouve = True
            nom_trouve = True
            break

    if not Matricule_trouve:
        messagebox.showerror("Erreur de saisie", "Matricule non trouvé dans la base de données.")
        return

 

def Changer_la_taille_de_la_fenetre(): # Fonction pour changer la taille de la fenêtre pour scanner les balises
    App_Scan.geometry("1000x350")
    largeur_ecran = App_Scan.winfo_screenwidth()
    longueur_ecran = App_Scan.winfo_screenheight()
    largeur=1000
    longueur=350
    x = (largeur_ecran/2) - (largeur/2)
    y = (longueur_ecran/2) - (longueur/2)
    App_Scan.geometry('%dx%d+%d+%d' % (largeur, longueur, x, y))

def Afficher_Frame_Scan ():
    Afficher_Matricule_Nom()
    if nom_trouve and Matricule_trouve : # Si le nom et le matricule sont trouvés dans la base de données.
        Frame_Scan.tkraise() # Afficher la frame pour scanner les balises
        Changer_la_taille_de_la_fenetre() # Et changer sa taille
    else:
        messagebox.showerror("Erreur", "Veuillez entrer un matricule valide")



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

Bouton_Valider = Button(Frame_Matricule, text="Valider", command=Afficher_Frame_Scan, bg="grey") 
Bouton_Valider.place(x=300, y=70)


# Centrer  la fenêtre 
largeur_ecran = App_Scan.winfo_screenwidth()
longueur_ecran = App_Scan.winfo_screenheight()
largeur=400
longueur=100
x = (largeur_ecran/2) - (largeur/2)
y = (longueur_ecran/2) - (longueur/2)
App_Scan.geometry('%dx%d+%d+%d' % (largeur, longueur, x, y))

Frame_Scan = Frame(App_Scan)
Frame_Scan.place(x=0, y=0, relwidth=1, relheight=1)
DataMatrix_Carte = StringVar()
DataMatrix_Batterie = StringVar()

Image_Asteelflash = PhotoImage(file=resource_path("Images\\Asteelflash.png"))
Image_Asteelflash_reduite = Image_Asteelflash.subsample(3,3)
Label_Asteelflash_image = Label(Frame_Scan, image=Image_Asteelflash_reduite)
Label_Asteelflash_image.place(x=3, y=2)

Nom_utilisateur_title = Label (Frame_Scan, text=f"Nom : {nom}",font= ("Calibri", 10))
Nom_utilisateur_title.place(x=800, y=10)
Prenom_utilisateur_title = Label(Frame_Scan, text=f"Prenom : {prenom}", font=("Calibri", 10)) 
Prenom_utilisateur_title.place(x=782, y=30)
Matricule_trouve_title = Label (Frame_Scan, text=f"Matricule : {BDD_matricule}",font= ("Calibri", 10))
Matricule_trouve_title.place(x=770, y=50)

DataMatrix_Carte_title = Label (Frame_Scan, text="CARTE :",font=("Arial", 24))
DataMatrix_Carte_title.place(x=55, y= 100)
DataMatrix_Carte_Entry = Entry (Frame_Scan, textvariable= DataMatrix_Carte, font=("Calibri", 24), width=48)
DataMatrix_Carte_Entry.place(x= 200, y=95)

DataMatrix_Batterie_title = Label(Frame_Scan, text="BATTERIE :", font=("Arial", 24))
DataMatrix_Batterie_title.place(x=10, y= 200)
DataMatrix_Batterie_Entry = Entry(Frame_Scan, textvariable= DataMatrix_Batterie, font=("Calibri", 24), width=48)
DataMatrix_Batterie_Entry.place(x= 200, y=195)

App_Scan.iconbitmap(resource_path('Images\\Asteelflash_icon.ico'))

Frame_Matricule.tkraise()
App_Scan.mainloop()