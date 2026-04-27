import sqlite3
import json
import os

DB_NAME = "climatometre.db"
DATA_FILE = "membres.json"

def create_schema(cursor):
    print("--- Création des tables ---")
    cursor.execute('DROP TABLE IF EXISTS releves_meteo')
    cursor.execute('DROP TABLE IF EXISTS residences')
    cursor.execute('DROP TABLE IF EXISTS etudiants')

    cursor.execute('''
    CREATE TABLE etudiants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        prenom TEXT NOT NULL
    )''')

    cursor.execute('''
    CREATE TABLE residences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        etudiant_id INTEGER,
        ville TEXT NOT NULL,
        adresse TEXT,
        type TEXT,
        date_debut TEXT,
        date_fin TEXT,
        lat REAL,
        lon REAL,
        FOREIGN KEY (etudiant_id) REFERENCES etudiants(id)
    )''')

    cursor.execute('''
    CREATE TABLE releves_meteo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        residence_id INTEGER,
        date_releve DATETIME DEFAULT CURRENT_TIMESTAMP,
        temp REAL,
        humidite REAL,
        description TEXT,
        FOREIGN KEY (residence_id) REFERENCES residences(id)
    )''')

def import_data(cursor):
    if not os.path.exists(DATA_FILE):
        print("Erreur : membres.json introuvable.")
        return
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for membre in data:
        cursor.execute("INSERT INTO etudiants (nom, prenom) VALUES (?, ?)", 
                       (membre['nom'], membre['prenom']))
        e_id = cursor.lastrowid
        rp = membre['residence_principale']
        cursor.execute('''
            INSERT INTO residences (etudiant_id, ville, type, date_debut, date_fin) 
            VALUES (?, ?, ?, ?, ?)
        ''', (e_id, rp['ville'], 'Principale', rp['debut'], rp.get('fin')))  # ← correction ici
        print(f"Ajouté : {membre['prenom']} {membre['nom']}")

def main():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        create_schema(cursor)
        import_data(cursor)
        conn.commit()
        print("\n[OK] Base de données initialisée avec colonnes GPS.")
    except Exception as e:
        conn.rollback()
        print(f"\n[ERREUR] : {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()