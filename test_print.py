import re
import datetime
from zebra import Zebra
from configparser import ConfigParser
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))) 
    return os.path.join(base_path, relative_path)

configprinterini = resource_path("config\\config_print.ini")
config = ConfigParser(interpolation= None)
config.read(configprinterini)

FICHIER_PRN = config['CHEMINS']['FICHIER_PRN'] # Fichier PNR
NOM_IMPRIMANTE = config['IMPRIMANTE']['NOM_IMPRIMANTE'] # Nom de l'imprimante
DATAM_GAUCHE_SKELETON = config['IMPRESSION']['DATAMATRIXBOX'] # %LEFT%
DATAM_DROITE_SKELETON = config['IMPRESSION']['DATAMATRIXCONTENT'] # %RIGHT%
PNR_SKELETON = config['IMPRESSION']['PNR'] # %PNR% 
SER_SKELETON = config['IMPRESSION']['SER'] # %SER%
CSN_SKELETON = config['IMPRESSION']['CSN'] # %CSN%
DATAM_DROITE_TEST = config['IMPRESSION']['DATAMATRIXCONTENT_TEST']
DATAM_GAUCHE_TEST = config['IMPRESSION']['DATAMATRIXBOX_TEST']

ser_skeleton = None
pnr_skeleton = None
CSN_skeleton = None
datamgauche_skeleton = None
datamdroite_skeleton =None

pnr_datam = None
ser_datam = None
csn_datam = None
datamdroite = None
datamgauche = None

nouveau_fichier = None

aujourdhui = datetime.datetime.now() 

def Recherche_Infos_DataMatrix():
    global pnr_datam, ser_datam, csn_datam
    pnr_datam = DATAM_GAUCHE_TEST[42:53] # A modifier avec le DATAM IHM
    print(pnr_datam)
    ser_datam = DATAM_GAUCHE_TEST[:12] # A modifier avec le DATAM IHM
    print(ser_datam)
    csn_datam = DATAM_DROITE_TEST[52:58] # A modifier avec le DATAM IHM
    print(csn_datam)


def Recherche_Infos_SKELETON():
    global pnr_skeleton, ser_skeleton, CSN_skeleton, datamgauche_skeleton, datamdroite_skeleton
    global pnr_datam, ser_datam, csn_datam, datamdroite, datamgauche
    global nouveau_fichier

    with open(FICHIER_PRN, "r") as fichier:
        contenu = fichier.read()
    nouveau_contenu = contenu  

    # PNR 
    for ligne in contenu.splitlines():
        if PNR_SKELETON in ligne:
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
            print("DataMGauche :", datamgauche_skeleton)
            nouveau_contenu = nouveau_contenu.replace(datamgauche_skeleton, DATAM_GAUCHE_TEST)
            break

    # DATAMATRIX DROITE 
    for ligne in contenu.splitlines():
        if DATAM_DROITE_SKELETON in ligne:
            datamdroite_skeleton = re.search(r"\^FD(.+?)\^FS", ligne).group(1)
            print("DataMDroite :", datamdroite_skeleton)
            nouveau_contenu = nouveau_contenu.replace(datamdroite_skeleton, DATAM_DROITE_TEST)
            break

 
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nouveau_fichier = os.path.join(os.path.dirname(FICHIER_PRN), f"{timestamp}.prn")
    with open(nouveau_fichier, "w") as fichier:
        fichier.write(nouveau_contenu)
    print("nouveau :", nouveau_fichier)


def Impression() : 
    global nouveau_fichier
    ouvrir_prn = open(nouveau_fichier)
    lire_prn = ouvrir_prn.read()
    print(lire_prn)
    ouvrir_prn.close()
    z = Zebra()
    try: 
        z.getqueues().index(NOM_IMPRIMANTE)
    except ValueError : 
        print(f"Imprimante non trouvée {NOM_IMPRIMANTE}" )
    else : 
        z.setqueue(NOM_IMPRIMANTE)
        imprimer = lire_prn
        z.output(imprimer)
        



Recherche_Infos_DataMatrix()
Recherche_Infos_SKELETON()
Impression()

    




