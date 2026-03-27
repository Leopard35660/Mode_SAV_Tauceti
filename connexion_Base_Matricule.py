import pyodbc
from configparser import ConfigParser
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))) 
    return os.path.join(base_path, relative_path)


configscanini = resource_path("config\\config_ScanDataM.ini")
config = ConfigParser()
config.read(configscanini)

CHEMIN_DATABASE = config['CHEMINS']['CHEMIN_DATABASE'] 
NOM_DATABASE = config['NOM']['NOM_DATABASE']

try : 
    connexion = pyodbc.connect(r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"r"DBQ=" + CHEMIN_DATABASE + "\\" + NOM_DATABASE)
    cursor = connexion.cursor()
    cursor.execute("SELECT matricule, name FROM t_users")
    row = cursor.fetchall()  # Récupère TOUS les résultats dans row
    # data_right = connexion.cursor()
    # data_right.execute("SELECT right FROM t_users")
    # row_right = data_right.fetchall()
    
except Exception as e:
    print("Erreur lors de la connexion à la base de données : ", e)
    row = []
    # row_right = []

