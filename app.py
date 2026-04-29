from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sqlite3
import statistics
import threading
import time
import update_weather

app = Flask(__name__)
DB_NAME = "climatometre.db"
weather_thread_started = False
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-change-me')

def get_db_connection():
    """Établit la connexion à la base SQLite."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/map')
def index():
    # require login for map
    if not session.get('user_id'):
        return redirect(url_for('home'))

    conn = get_db_connection()
    
    # Requête complète : on récupère tout sans filtre WHERE restrictif
    # pour éviter de rater les "Principale" avec majuscule
    query = '''
        SELECT e.id as et_id, e.nom, e.prenom,
               r.id as res_id, r.ville, r.adresse, r.lat, r.lon, r.type,
               m.temp, m.description
        FROM etudiants e
        JOIN residences r ON e.id = r.etudiant_id
        LEFT JOIN releves_meteo m
          ON m.id = (
              SELECT id
              FROM releves_meteo
              WHERE residence_id = r.id
              ORDER BY date_releve DESC
              LIMIT 1
          )
        ORDER BY e.nom ASC, r.type DESC
    '''
    rows = conn.execute(query).fetchall()
    
    releves = []
    points_gps = []
    temps_liste = []
    grouped_addresses = {}
    grouped_cities = {}

    for row in rows:
        # On ajoute la ligne au tableau
        releves.append(row)
        
        # Collecte des températures pour la médiane
        if row['temp'] is not None:
            temps_liste.append(row['temp'])
        
        # On nettoie le type pour le test (enlève espaces et majuscules)
        type_clean = str(row['type']).lower().strip()
        student_key = f"{row['prenom']} {row['nom']}"
        icone = "🏠" if type_clean == "principale" else "🏢"
        student_info = f"{icone} {student_key} ({type_clean}) - {row['temp'] or '--'}°C"

        # Regroupement par ville pour la liste
        raw_city = (row['ville'] or '').strip()
        # key used for grouping (case-insensitive), display uses title-cased city name
        city_key = raw_city.lower() if raw_city else 'adresse inconnue'
        city_display = raw_city.title() if raw_city else 'Adresse inconnue'
        if city_key not in grouped_cities:
            grouped_cities[city_key] = {
                'ville': city_display,
                'students': {}
            }
        grouped_cities[city_key]['students'][student_key] = {
            'info': student_info,
            'et_id': row['et_id'],
            'adresse': row['adresse'] or ''
        }

        # Préparation des points pour la carte par adresse
        if row['lat'] and row['lon']:
            adresse_propre = row['adresse'].strip() if row['adresse'] and str(row['adresse']).strip() else None
            if adresse_propre:
                key = (row['lat'], row['lon'], adresse_propre)
                address_label = adresse_propre
            else:
                # use normalized city display name when adresse is missing
                key = (row['lat'], row['lon'], f"{city_display} - résidence {row['res_id']}")
                address_label = f"{city_display} (adresse inconnue #{row['res_id']})"

            popup_student = f"{icone} {student_key} ({type_clean}) - {row['temp'] or '--'}°C"
            
            if key not in grouped_addresses:
                grouped_addresses[key] = {
                    'lat': row['lat'],
                    'lon': row['lon'],
                    'ville': row['ville'],
                    'adresse': address_label,
                    'students': {}
                }
            # store popup text and etudiant id for later association with markers
            grouped_addresses[key]['students'][student_key] = {
                'popup': popup_student,
                'et_id': row['et_id']
            }

    # Créer les points_gps avec un marqueur par adresse
    for point in grouped_addresses.values():
        # build ordered lists of popup lines, names and ids
        student_items = sorted(point['students'].items(), key=lambda kv: kv[0])
        student_list = [v['popup'] for k, v in student_items]
        student_names = [k for k, v in student_items]
        student_ids = [v['et_id'] for k, v in student_items]
        popup_content = (
            f"<b>{point['adresse']}</b><br><small>{point['ville']}</small><br>"
            + "<br>".join(student_list)
        )
        points_gps.append({
            'lat': point['lat'],
            'lon': point['lon'],
            'popup': popup_content,
            'city': point['ville'],
            'adresse': point['adresse'],
            'student_names': student_names,
            'student_ids': student_ids,
            'search': ' '.join([str(point['ville'] or ''), str(point['adresse'] or '')] + student_names).lower()
        })

    # Calcul de la médiane via statistics
    mediane = round(statistics.median(temps_liste), 2) if temps_liste else 0
            
    conn.close()
    return render_template('index.html', 
                           releves=releves, 
                           mediane=mediane, 
                           points=points_gps,
                           grouped_cities=list(grouped_cities.values()))


@app.route('/')
def home():
    """Page d'accueil : affiche la page de connexion (login)."""
    return render_template('login.html')


def get_user_by_username(username):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return user


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            flash('Identifiant et mot de passe requis')
            return redirect(url_for('home'))

        # create user
        pw_hash = generate_password_hash(password)
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, pw_hash))
            conn.commit()
        except Exception as e:
            conn.close()
            flash('Impossible de créer le compte (identifiant peut-être déjà utilisé)')
            return redirect(url_for('home'))
        conn.close()
        flash('Compte créé. Vous pouvez vous connecter.')
        return redirect(url_for('home'))
    return render_template('creation.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form.get('username')
    password = request.form.get('password')
    if not username or not password:
        flash('Identifiant et mot de passe requis')
        return redirect(url_for('home'))

    user = get_user_by_username(username)
    if not user:
        flash('Identifiant inexistant')
        return redirect(url_for('home'))
    
    if not check_password_hash(user['password_hash'], password):
        flash('Mot de passe incorrect')
        return redirect(url_for('home'))

    # success
    session.clear()
    session['user_id'] = user['id']
    session['username'] = user['username']
    flash('Connecté')
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.clear()
    flash('Déconnecté', 'success')
    return redirect(url_for('home'))

def get_current_user():
    """Retourne l'utilisateur actuel ou None."""
    if session.get('user_id'):
        user = get_user_by_username(session.get('username', ''))
        return user
    return None

def admin_required(func):
    """Décorateur pour vérifier que l'utilisateur est admin."""
    from functools import wraps
    @wraps(func)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user or user['role'] != 'admin':
            flash('Accès réservé aux administrateurs', 'error')
            return redirect(url_for('home'))
        return func(*args, **kwargs)
    return decorated_function

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'GET':
        return render_template('forgot_password.html')

    username = request.form.get('username')
    if not username:
        flash('Identifiant requis', 'error')
        return redirect(url_for('forgot_password'))

    user = get_user_by_username(username)
    if not user:
        flash('Identifiant inexistant', 'error')
        return redirect(url_for('forgot_password'))

    # Store reset token in session
    session['password_reset_username'] = username
    flash('Veuillez entrer votre nouveau mot de passe', 'success')
    return redirect(url_for('reset_password'))

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if 'password_reset_username' not in session:
        flash('Session expirée. Recommencez', 'error')
        return redirect(url_for('forgot_password'))

    if request.method == 'GET':
        return render_template('reset_password.html')

    password = request.form.get('password')
    password_confirm = request.form.get('password_confirm')

    if not password or not password_confirm:
        flash('Mots de passe requis', 'error')
        return redirect(url_for('reset_password'))

    if password != password_confirm:
        flash('Les mots de passe ne correspondent pas', 'error')
        return redirect(url_for('reset_password'))

    if len(password) < 4:
        flash('Le mot de passe doit contenir au moins 4 caractères', 'error')
        return redirect(url_for('reset_password'))

    # Update password
    username = session['password_reset_username']
    conn = get_db_connection()
    password_hash = generate_password_hash(password)
    conn.execute('UPDATE users SET password_hash = ? WHERE username = ?', (password_hash, username))
    conn.commit()
    conn.close()

    session.clear()
    flash('Mot de passe réinitialisé avec succès. Connectez-vous', 'success')
    return redirect(url_for('home'))

@app.route('/admin')
@admin_required
def admin():
    """Page tableau de bord admin - liste toutes les tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get list of all tables
    tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()
    
    table_info = []
    for table in tables:
        table_name = table['name']
        count = cursor.execute(f"SELECT COUNT(*) as cnt FROM {table_name}").fetchone()['cnt']
        table_info.append({
            'name': table_name,
            'count': count
        })
    
    conn.close()
    return render_template('admin.html', tables=table_info)

@app.route('/admin/table/<table_name>')
@admin_required
def admin_table(table_name):
    """Page détail pour une table admin."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Validation de sécurité : vérifier que la table existe
    tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name = ?", (table_name,)).fetchall()
    if not tables:
        flash('Table introuvable', 'error')
        conn.close()
        return redirect(url_for('admin'))
    
    # Get schema
    schema = cursor.execute(f"PRAGMA table_info({table_name})").fetchall()
    
    # Get data (limite à 200 lignes)
    data = cursor.execute(f"SELECT * FROM {table_name} LIMIT 200").fetchall()
    
    conn.close()
    return render_template('admin_table.html', 
                         table_name=table_name, 
                         schema=schema, 
                         data=data)

@app.context_processor
def inject_current_user():
    """Injecte l'utilisateur courant dans tous les templates."""
    return {'current_user': get_current_user()}

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
            primary_res_id = cursor.lastrowid
            
            # 3. Insertion résidence secondaire (si ville renseignée)
            secondary_res_id = None
            if ville_s and ville_s.strip():
                cursor.execute('''
                    INSERT INTO residences (etudiant_id, ville, adresse, type)
                    VALUES (?, ?, ?, 'secondaire')
                ''', (etudiant_id, ville_s, adresse_s))
                secondary_res_id = cursor.lastrowid
            
            conn.commit()
        except Exception as e:
            print(f"Erreur lors de l'ajout : {e}")
            conn.rollback()
        finally:
            conn.close()

        # Mise à jour automatique de la météo pour les nouvelles résidences
        try:
            update_weather.update_residence(primary_res_id, ville_p)
            if secondary_res_id:
                update_weather.update_residence(secondary_res_id, ville_s)
        except Exception as e:
            print(f"Erreur lors de la mise à jour météo automatique : {e}")
            # On redirige quand même même si la météo n'a pas pu se mettre à jour
        
        return redirect(url_for('index'))
        
    return render_template('ajouter.html')

@app.route('/modifier/<int:etudiant_id>', methods=['GET', 'POST'])
def modifier(etudiant_id):
    conn = get_db_connection()
    if request.method == 'POST':
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        ville_p = request.form.get('ville_p')
        adresse_p = request.form.get('adresse_p')
        ville_s = request.form.get('ville_s')
        adresse_s = request.form.get('adresse_s')
        secondary_res_id = request.form.get('secondary_res_id')

        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE etudiants SET nom = ?, prenom = ? WHERE id = ?",
                           (nom, prenom, etudiant_id))
            cursor.execute('''
                UPDATE residences
                SET ville = ?, adresse = ?
                WHERE etudiant_id = ? AND type = 'principale'
            ''', (ville_p, adresse_p, etudiant_id))

            if ville_s and ville_s.strip():
                if secondary_res_id:
                    cursor.execute('''
                        UPDATE residences
                        SET ville = ?, adresse = ?
                        WHERE id = ?
                    ''', (ville_s, adresse_s, secondary_res_id))
                else:
                    cursor.execute('''
                        INSERT INTO residences (etudiant_id, ville, adresse, type)
                        VALUES (?, ?, ?, 'secondaire')
                    ''', (etudiant_id, ville_s, adresse_s))
            else:
                if secondary_res_id:
                    cursor.execute('DELETE FROM residences WHERE id = ?', (secondary_res_id,))

            conn.commit()
        except Exception as e:
            print(f"Erreur lors de la modification : {e}")
            conn.rollback()
        finally:
            conn.close()

        try:
            conn2 = get_db_connection()
            cursor2 = conn2.cursor()
            cursor2.execute("SELECT id FROM residences WHERE etudiant_id = ? AND type = 'principale'", (etudiant_id,))
            primary_row = cursor2.fetchone()
            if primary_row:
                update_weather.update_residence(primary_row['id'], ville_p)

            cursor2.execute("SELECT id FROM residences WHERE etudiant_id = ? AND type = 'secondaire'", (etudiant_id,))
            secondary_row = cursor2.fetchone()
            if secondary_row and ville_s and ville_s.strip():
                update_weather.update_residence(secondary_row['id'], ville_s)
            conn2.close()
        except Exception as e:
            print(f"Erreur lors de la mise à jour météo après modification : {e}")

        return redirect(url_for('index'))

    student = conn.execute('SELECT * FROM etudiants WHERE id = ?', (etudiant_id,)).fetchone()
    residences = conn.execute('SELECT * FROM residences WHERE etudiant_id = ?', (etudiant_id,)).fetchall()
    conn.close()

    if not student:
        return redirect(url_for('index'))

    primary = None
    secondary = None
    for residence in residences:
        if residence['type'].lower().strip() == 'principale':
            primary = residence
        else:
            secondary = residence

    return render_template('modifier.html', student=student, primary=primary, secondary=secondary)

@app.before_request
def start_weather_updates():
    global weather_thread_started
    if not weather_thread_started:
        def weather_update_loop(interval=60):
            while True:
                try:
                    update_weather.update_all()
                except Exception as e:
                    print(f"Erreur boucle météo : {e}")
                time.sleep(interval)

        thread = threading.Thread(target=weather_update_loop, daemon=True)
        thread.start()
        weather_thread_started = True

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


@app.route('/api/etudiant/<int:etudiant_id>')
def api_etudiant(etudiant_id):
    """Renvoie les informations d'un étudiant (et ses résidences + dernier relevé) en JSON."""
    conn = get_db_connection()
    student = conn.execute('SELECT id, nom, prenom FROM etudiants WHERE id = ?', (etudiant_id,)).fetchone()
    if not student:
        conn.close()
        return jsonify({'error': 'Étudiant introuvable'}), 404

    rows = conn.execute('''
        SELECT r.id, r.ville, r.adresse, r.lat, r.lon, r.type,
               m.temp, m.description, m.date_releve
        FROM residences r
        LEFT JOIN releves_meteo m
          ON m.id = (
              SELECT id FROM releves_meteo
              WHERE residence_id = r.id
              ORDER BY date_releve DESC
              LIMIT 1
          )
        WHERE r.etudiant_id = ?
    ''', (etudiant_id,)).fetchall()

    residences = []
    for r in rows:
        residences.append({
            'id': r['id'],
            'ville': r['ville'],
            'adresse': r['adresse'],
            'lat': r['lat'],
            'lon': r['lon'],
            'type': r['type'],
            'temp': r['temp'],
            'description': r['description'],
            'date_releve': r['date_releve']
        })

    conn.close()
    return jsonify({
        'id': student['id'],
        'nom': student['nom'],
        'prenom': student['prenom'],
        'residences': residences
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)