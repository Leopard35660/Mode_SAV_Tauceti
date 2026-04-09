from configparser import ConfigParser
import os
import sys
import mysql.connector

#Le script se connecte à la base SQL tauceti : table t_products pour prendre les infos f_case et f_boxright


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
