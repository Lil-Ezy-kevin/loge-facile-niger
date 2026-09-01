import sqlite3
from config import Config

def get_db():
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS demandes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL, telephone TEXT NOT NULL,
        email TEXT, type_logement TEXT, budget TEXT,
        quartier TEXT, precisions TEXT,
        statut TEXT DEFAULT 'nouveau',
        date_soumission TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS propositions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL, telephone TEXT NOT NULL,
        type_logement TEXT, quartier TEXT,
        loyer TEXT, description TEXT,
        statut TEXT DEFAULT 'en_attente',
        date_soumission TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS fichiers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        proposition_id INTEGER NOT NULL,
        nom_fichier TEXT NOT NULL, type_fichier TEXT,
        date_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (proposition_id) REFERENCES propositions(id)
    )''')

    # Logements publies visibles par les visiteurs
    c.execute('''CREATE TABLE IF NOT EXISTS logements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titre TEXT NOT NULL,
        type_logement TEXT,
        quartier TEXT,
        ville TEXT DEFAULT 'Agadez',
        loyer TEXT,
        description TEXT,
        nb_pieces TEXT,
        surface TEXT,
        meuble INTEGER DEFAULT 0,
        disponible INTEGER DEFAULT 1,
        contact_bailleur TEXT,
        telephone_bailleur TEXT,
        proposition_id INTEGER,
        date_publication TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (proposition_id) REFERENCES propositions(id)
    )''')

    # Photos/videos des logements publies
    c.execute('''CREATE TABLE IF NOT EXISTS logement_photos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        logement_id INTEGER NOT NULL,
        nom_fichier TEXT NOT NULL,
        type_fichier TEXT DEFAULT 'image',
        est_principale INTEGER DEFAULT 0,
        FOREIGN KEY (logement_id) REFERENCES logements(id)
    )''')

    conn.commit()
    conn.close()
    print("Base de donnees initialisee.")

if __name__ == '__main__':
    init_db()
