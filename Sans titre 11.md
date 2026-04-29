
### Étape 2 : Exécuter les commandes

Ouvre ton terminal dans VS Code et tape ces commandes l'une après l'autre :

1. **`python init_db.py`** _(Ça réinitialise la base de données proprement)._
    
2. **`python import_csv_final.py`** _(C'est là que la magie opère : tes 53 noms vont défiler)._
    
3. **`python app.py`** _(Pour relancer le site)._
   
### Étape 3 : Un tout petit changement visuel (Optionnel)

Si tu veux voir les **dates** (2025, 2028, etc.) s'afficher dans la fiche de droite (comme sur ta photo `image_ef0e73.png`), fais ceci :

1. Ouvre ton fichier **`templates/index.html`**.
    
2. Cherche la ligne qui commence par `d.innerHTML = ...` (vers la fin du fichier).
    
3. Remplace-la par celle-ci pour inclure la période :
    

JavaScript

```
d.innerHTML = `<strong>${(r.type||'résidence')}</strong>: ${r.ville || ''}${r.adresse ? ', '+r.adresse : ''}<br>` +
              `<small style="color:#aaa;">Période : ${r.date_debut || '-'} à ${r.date_fin || '-'}</small>` +
              (r.temp !== null ? ` — <b>${r.temp}°C</b>` : '');
```


Lance la commande : `python import_secondaire.py`