from configparser import ConfigParser
import os
import sys
import mysql.connector

#Le script se connecte à la base SQL tauceti : table t_users pour prendre les infos d'utilisateurs

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


try : 
    db = mysql.connector.connect(user =USER_DATABASE, password=PASSWORD_DATABASE, host=SERVEUR_DATABASE, database=DATABASE)
    cursor = db.cursor()
    #Selectionner toutes les infos de la table t_users
    cursor.execute("SELECT * FROM t_users")
    row = cursor.fetchall()  # Récupère TOUS les résultats dans la base
    print("row", row)
    # row est une liste de toutes les valeurs 
    # elle est appélée dans le script Scan_DataMatrix.py
except Exception as e:
    print("Erreur lors de la connexion à la base de données : ", e)
    row = []
