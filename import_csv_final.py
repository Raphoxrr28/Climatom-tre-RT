import csv
import sqlite3
import update_weather 

DB_NAME = "climatometre.db"

def importer():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # NETTOYAGE : On vide tout pour recommencer proprement
    cursor.execute("DELETE FROM releves_meteo")
    cursor.execute("DELETE FROM residences")
    cursor.execute("DELETE FROM etudiants")

    # IMPORTANT : Voici l'ordre exact de tes colonnes CSV
    colonnes = ['Nom', 'Prenom', 'Ville', 'Adresse', 'debut', 'fin']

    try:
        with open('etudiants1.csv', newline='', encoding='utf-8') as f:
            # On dit au lecteur d'utiliser nos titres "colonnes"
            reader = csv.DictReader(f, fieldnames=colonnes)
            
            for row in reader:
                # 1. Insertion de l'étudiant
                nom = row['Nom'].strip().upper()
                prenom = row['Prenom'].strip()
                cursor.execute("INSERT INTO etudiants (nom, prenom) VALUES (?, ?)", (nom, prenom))
                etudiant_id = cursor.lastrowid

                # 2. Récupération des dates (on garde le tiret SEULEMENT si c'est vide ou si c'est un tiret)
                date_debut = row['debut'].strip() if row['debut'] and row['debut'].strip() != "" else "-"
                date_fin = row['fin'].strip() if row['fin'] and row['fin'].strip() != "" else "-"

                # 3. Insertion de la résidence
                cursor.execute('''
                    INSERT INTO residences (etudiant_id, ville, adresse, type, date_debut, date_fin)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    etudiant_id, 
                    row['Ville'].strip(), 
                    row['Adresse'].strip(), 
                    'Principale', 
                    date_debut, 
                    date_fin
                ))
                
                res_id = cursor.lastrowid
                print(f"Import de : {prenom} {nom} | Dates: {date_debut} à {date_fin}")

                # 4. Météo
                try:
                    update_weather.update_residence(res_id, row['Ville'].strip())
                except:
                    pass 

        conn.commit()
        print("\n--- TERMINE : Tes données sont maintenant correctes ! ---")
    except Exception as e:
        print(f"Erreur : {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    importer()