from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import statistics

app = Flask(__name__)
DB_NAME = "climatometre.db"

def get_db_connection():
    """Établit la connexion à la base SQLite."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    
    # Requête complète : on récupère tout sans filtre WHERE restrictif
    # pour éviter de rater les "Principale" avec majuscule
    query = '''
        SELECT e.id as et_id, e.nom, e.prenom, 
               r.id as res_id, r.ville, r.lat, r.lon, r.type,
               m.temp, m.description
        FROM etudiants e
        JOIN residences r ON e.id = r.etudiant_id
        LEFT JOIN releves_meteo m ON r.id = m.residence_id
        ORDER BY e.nom ASC, r.type DESC
    '''
    rows = conn.execute(query).fetchall()
    
    releves = []
    points_gps = []
    temps_liste = []

    for row in rows:
        # On ajoute la ligne au tableau
        releves.append(row)
        
        # On nettoie le type pour le test (enlève espaces et majuscules)
        type_clean = str(row['type']).lower().strip()
        
        # Préparation des points pour la carte (si coordonnées présentes)
        if row['lat'] and row['lon']:
            icone = "🏠" if type_clean == "principale" else "🏢"
            points_gps.append({
                "lat": row['lat'],
                "lon": row['lon'],
                "popup": f"<b>{icone} {row['prenom']} {row['nom']}</b><br>{row['ville']} ({type_clean})<br>{row['temp'] or '--'}°C"
            })
        
        # Collecte des températures pour la médiane
        if row['temp'] is not None:
            temps_liste.append(row['temp'])

    # Calcul de la médiane via statistics
    mediane = round(statistics.median(temps_liste), 2) if temps_liste else 0
            
    conn.close()
    return render_template('index.html', 
                           releves=releves, 
                           mediane=mediane, 
                           points=points_gps)

@app.route('/ajouter', methods=['GET', 'POST'])
def ajouter():
    if request.method == 'POST':
        # Récupération des données du formulaire HTML
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        ville_p = request.form.get('ville_p')
        adresse_p = request.form.get('adresse_p')
        ville_s = request.form.get('ville_s')
        adresse_s = request.form.get('adresse_s')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 1. Insertion de l'étudiant
            cursor.execute("INSERT INTO etudiants (nom, prenom) VALUES (?, ?)", (nom, prenom))
            etudiant_id = cursor.lastrowid
            
            # 2. Insertion résidence principale (obligatoire)
            cursor.execute('''
                INSERT INTO residences (etudiant_id, ville, adresse, type)
                VALUES (?, ?, ?, 'principale')
            ''', (etudiant_id, ville_p, adresse_p))
            
            # 3. Insertion résidence secondaire (si ville renseignée)
            if ville_s and ville_s.strip():
                cursor.execute('''
                    INSERT INTO residences (etudiant_id, ville, adresse, type)
                    VALUES (?, ?, ?, 'secondaire')
                ''', (etudiant_id, ville_s, adresse_s))
            
            conn.commit()
        except Exception as e:
            print(f"Erreur lors de l'ajout : {e}")
            conn.rollback()
        finally:
            conn.close()
            
        return redirect(url_for('index'))
        
    return render_template('ajouter.html')

@app.route('/supprimer/<int:id>')
def supprimer(id):
    """Supprime un étudiant et ses résidences liées."""
    conn = get_db_connection()
    try:
        conn.execute("DELETE FROM residences WHERE etudiant_id = ?", (id,))
        conn.execute("DELETE FROM etudiants WHERE id = ?", (id,))
        conn.commit()
    except Exception as e:
        print(f"Erreur suppression : {e}")
    finally:
        conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)