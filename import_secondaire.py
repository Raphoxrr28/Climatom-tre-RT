import csv
import sqlite3
import update_weather 

DB_NAME = "climatometre.db"

def importer_secondaires():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Ordre des colonnes de ton 2ème CSV (à vérifier selon ton fichier)
    colonnes = ['Nom', 'Prenom', 'Ville', 'Adresse', 'debut', 'fin']

    try:
        with open('etudiants2.csv', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f, fieldnames=colonnes)
            
            for row in reader:
                nom = row['Nom'].strip().upper()
                prenom = row['Prenom'].strip()

                # 1. On cherche l'ID de l'étudiant déjà existant
                cursor.execute("SELECT id FROM etudiants WHERE nom = ? AND prenom = ?", (nom, prenom))
                resultat = cursor.fetchone()

                if resultat:
                    etudiant_id = resultat[0]
                    
                    # 2. On insère la résidence SECONDAIRE
                    cursor.execute('''
                        INSERT INTO residences (etudiant_id, ville, adresse, type, date_debut, date_fin)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        etudiant_id, 
                        row['Ville'].strip(), 
                        row['Adresse'].strip(), 
                        'Secondaire', 
                        row['debut'].strip() or "-", 
                        row['fin'].strip() or "-"
                    ))
                    
                    res_id = cursor.lastrowid
                    print(f"Résidence secondaire ajoutée pour : {prenom} {nom}")

                    # 3. Mise à jour météo/GPS
                    try:
                        update_weather.update_residence(res_id, row['Ville'].strip())
                    except:
                        pass
                else:
                    print(f"⚠️ Étudiant non trouvé : {prenom} {nom}. Impossible d'ajouter la secondaire.")

        conn.commit()
        print("\n--- TERMINE : Les résidences secondaires ont été ajoutées ! ---")
    except Exception as e:
        print(f"Erreur : {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    importer_secondaires()