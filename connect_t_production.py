from configparser import ConfigParser
import os
import sys
import mysql.connector


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
    cursor.execute("SELECT id_production, lbl_carte, lbl_batterie, lbl_boitier FROM t_production")
    t_production = cursor.fetchall()  # Récupère TOUS les résultats dans la base
except Exception as e:
    print("Erreur lors de la connexion à la base de données : ", e)
    t_production = []


