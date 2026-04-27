import sqlite3
import requests

# --- CONFIGURATION ---
API_KEY = "TA_CLE_API_ICI" 
DB_NAME = "climatometre.db"

def get_weather(ville):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={ville}&appid={"0814e8d3aebacae244d30c3b2ee748f0"}&units=metric&lang=fr"
    print(f"-> Appel API pour {ville}...") 
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
        else:
            print(f"Erreur API ({r.status_code}) pour {ville}")
            return None
    except Exception as e:
        print(f"Erreur connexion : {e}")
        return None

def update_all():
    print("--- DÉBUT DE LA MISE À JOUR ---")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, ville FROM residences")
    residences = cursor.fetchall()
    print(f"Villes trouvées dans la base : {len(residences)}")

    for r_id, ville in residences:
        data = get_weather(ville)
        if data:
            temp = data['main']['temp']
            hum = data['main']['humidity']
            desc = data['weather'][0]['description']
            lat = data['coord']['lat']
            lon = data['coord']['lon']

            cursor.execute("INSERT INTO releves_meteo (residence_id, temp, humidite, description) VALUES (?,?,?,?)",
                           (r_id, temp, hum, desc))
            
            cursor.execute("UPDATE residences SET lat = ?, lon = ? WHERE id = ?", (lat, lon, r_id))
            
            print(f"✅ {ville} mis à jour : {temp}°C")

    conn.commit()
    conn.close()
    print("--- FIN DE LA MISE À JOUR ---")

# ON APPELLE LA FONCTION DIRECTEMENT ICI SANS CONDITION
update_all()