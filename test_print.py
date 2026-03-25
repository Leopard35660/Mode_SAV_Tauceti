from zebra import Zebra
from configparser import ConfigParser
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))) 
    return os.path.join(base_path, relative_path)

configprinterini = resource_path("config\\config_print.ini")
config = ConfigParser()
config.read(configprinterini)

FICHIER_PRN = config['CHEMINS']['FICHIER_PRN'] 
NOM_IMPRIMANTE = config['IMPRIMANTE']['NOM_IMPRIMANTE']

Ouvrir_PRN = open(FICHIER_PRN) # Ouverture du fichier.prn
Lire_PRN = Ouvrir_PRN.read() #Lecture du contenu.prn 

z = Zebra()

try : 
    z.getqueues().index(NOM_IMPRIMANTE)
    
except ValueError : 
    print("L'imprimante n'a pas été trouvée: " + NOM_IMPRIMANTE)
else:
    z.setqueue(NOM_IMPRIMANTE)
    impression = Lire_PRN
    z.output(impression)
    print("L'impression est réalisée")
    Ouvrir_PRN.close()
