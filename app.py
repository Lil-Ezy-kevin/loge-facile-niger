import os
import sys
import uuid

# Fix encodage UTF-8 sur Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    os.environ['PYTHONUTF8'] = '1'

from flask import Flask, request, jsonify, session, redirect, url_for, render_template, render_template_string
from werkzeug.utils import secure_filename
from config import Config
from database import get_db, init_db
from notifications import (
    notifier_nouvelle_demande, notifier_nouvelle_proposition,
    notifier_whatsapp_demande, notifier_whatsapp_proposition
)

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

# --- HELPERS --------------------------------------------------------------------

def extension_autorisee(nom):
    ext = nom.rsplit('.', 1)[-1].lower() if '.' in nom else ''
    return ext in Config.ALLOWED_EXTENSIONS

def sauvegarder_fichier(fichier):
    if fichier and extension_autorisee(fichier.filename):
        ext = fichier.filename.rsplit('.', 1)[-1].lower()
        nom_unique = f"{uuid.uuid4().hex}.{ext}"
        chemin = os.path.join(Config.UPLOAD_FOLDER, nom_unique)
        fichier.save(chemin)
        type_f = 'video' if ext in {'mp4', 'mov', 'avi'} else 'image'
        return nom_unique, type_f
    return None, None

# --- FRONTEND --------------------------------------------------------------------

@app.route('/')
def index():
    return app.send_static_file('index.html')

# --- API PUBLIQUE : LOGEMENTS ----------------------------------------------------

@app.route('/api/logements')
def api_logements():
    """Retourne tous les logements publies et disponibles."""
    conn = get_db()
    logements = conn.execute('''
        SELECT l.*,
               GROUP_CONCAT(p.nom_fichier || '|' || p.type_fichier || '|' || p.est_principale) as photos_raw
        FROM logements l
        LEFT JOIN logement_photos p ON p.logement_id = l.id
        WHERE l.disponible = 1
        GROUP BY l.id
        ORDER BY l.date_publication DESC
    ''').fetchall()
    conn.close()

    result = []
    for l in logements:
        photos = []
        if l['photos_raw']:
            for item in l['photos_raw'].split(','):
                parts = item.split('|')
                if len(parts) == 3:
                    photos.append({
                        'nom': parts[0],
                        'type': parts[1],
                        'principale': parts[2] == '1',
                        'url': f"/static/uploads/{parts[0]}"
                    })
        result.append({
            'id': l['id'],
            'titre': l['titre'],
            'type_logement': l['type_logement'],
            'quartier': l['quartier'],
            'ville': l['ville'],
            'loyer': l['loyer'],
            'description': l['description'],
            'nb_pieces': l['nb_pieces'],
            'surface': l['surface'],
            'meuble': bool(l['meuble']),
            'photos': photos,
            'date_publication': l['date_publication']
        })
    return jsonify(result)

# --- API : DEMANDE LOCATAIRE -----------------------------------------------------

@app.route('/api/demande', methods=['POST'])
def soumettre_demande():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Donnees manquantes.'}), 400
        nom = data.get('nom', '').strip()
        telephone = data.get('telephone', '').strip()
        if not nom or not telephone:
            return jsonify({'success': False, 'message': 'Nom et telephone obligatoires.'}), 400
        conn = get_db()
        conn.execute(
            'INSERT INTO demandes (nom,telephone,email,type_logement,budget,quartier,precisions) VALUES (?,?,?,?,?,?,?)',
            (nom, telephone, data.get('email',''), data.get('type_logement',''),
             data.get('budget',''), data.get('quartier',''), data.get('precisions',''))
        )
        conn.commit()
        conn.close()
        notifier_nouvelle_demande(data)
        notifier_whatsapp_demande(data)
        return jsonify({'success': True, 'message': 'Demande envoyee !'})
    except Exception as e:
        print(f"[ERREUR demande] {e}")
        return jsonify({'success': False, 'message': 'Erreur serveur.'}), 500

# --- API : PROPOSITION PROPRIETAIRE ---------------------------------------------

@app.route('/api/proposition', methods=['POST'])
def soumettre_proposition():
    try:
        nom = request.form.get('nom', '').strip()
        telephone = request.form.get('telephone', '').strip()
        if not nom or not telephone:
            return jsonify({'success': False, 'message': 'Nom et telephone obligatoires.'}), 400
        data = {
            'nom': nom, 'telephone': telephone,
            'type_logement': request.form.get('type_logement', ''),
            'quartier': request.form.get('quartier', ''),
            'loyer': request.form.get('loyer', ''),
            'description': request.form.get('description', ''),
        }
        conn = get_db()
        cursor = conn.execute(
            'INSERT INTO propositions (nom,telephone,type_logement,quartier,loyer,description) VALUES (?,?,?,?,?,?)',
            (data['nom'], data['telephone'], data['type_logement'],
             data['quartier'], data['loyer'], data['description'])
        )
        prop_id = cursor.lastrowid
        fichiers_uploades = []
        for fichier in request.files.getlist('fichiers')[:10]:
            nom_f, type_f = sauvegarder_fichier(fichier)
            if nom_f:
                conn.execute('INSERT INTO fichiers (proposition_id,nom_fichier,type_fichier) VALUES (?,?,?)',
                             (prop_id, nom_f, type_f))
                fichiers_uploades.append({'nom': nom_f, 'type': type_f})
        conn.commit()
        conn.close()
        notifier_nouvelle_proposition(data, fichiers_uploades)
        notifier_whatsapp_proposition(data, len(fichiers_uploades))
        return jsonify({'success': True, 'message': 'Proposition soumise !'})
    except Exception as e:
        print(f"[ERREUR proposition] {e}")
        return jsonify({'success': False, 'message': 'Erreur serveur.'}), 500

# --- ADMIN : AUTH ----------------------------------------------------------------

# login -> templates/login.html

@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        if (request.form.get('username') == Config.ADMIN_USERNAME and
                request.form.get('password') == Config.ADMIN_PASSWORD):
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        error = 'Identifiants incorrects.'
    return render_template("login.html", error=error)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

# --- ADMIN : DASHBOARD ----------------------------------------------------------

# dashboard -> templates/dashboard.html

@app.route('/admin')
@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    conn = get_db()
    demandes = conn.execute('SELECT * FROM demandes ORDER BY date_soumission DESC').fetchall()
    propositions = conn.execute('''
        SELECT p.*, COUNT(f.id) as nb_fichiers FROM propositions p
        LEFT JOIN fichiers f ON f.proposition_id = p.id
        GROUP BY p.id ORDER BY p.date_soumission DESC
    ''').fetchall()
    logements_raw = conn.execute('''
        SELECT l.*,
               COUNT(DISTINCT p.id) as nb_photos,
               MAX(CASE WHEN p.est_principale=1 THEN p.nom_fichier END) as photo_principale,
               MIN(p.nom_fichier) as premiere_photo
        FROM logements l
        LEFT JOIN logement_photos p ON p.logement_id = l.id
        GROUP BY l.id ORDER BY l.date_publication DESC
    ''').fetchall()

    # Enrichir photo_principale
    logements = []
    for l in logements_raw:
        d = dict(l)
        d['photo_principale'] = d['photo_principale'] or d['premiere_photo']
        logements.append(d)

    nb_nouvelles = conn.execute("SELECT COUNT(*) FROM demandes WHERE statut='nouveau'").fetchone()[0]
    nb_attente   = conn.execute("SELECT COUNT(*) FROM propositions WHERE statut='en_attente'").fetchone()[0]
    conn.close()
    return render_template("dashboard.html",
        demandes=demandes, propositions=propositions, logements=logements,
        nb_demandes=len(demandes), nb_nouvelles=nb_nouvelles,
        nb_propositions=len(propositions), nb_attente=nb_attente,
        nb_logements=len(logements))

# --- ADMIN : API LOGEMENTS -------------------------------------------------------

@app.route('/admin/api/logement', methods=['POST'])
def admin_publier_logement():
    if not session.get('admin'):
        return jsonify({'success': False}), 401
    try:
        titre = request.form.get('titre', '').strip()
        if not titre:
            return jsonify({'success': False, 'message': 'Titre obligatoire.'})
        conn = get_db()
        cursor = conn.execute('''
            INSERT INTO logements (titre, type_logement, quartier, ville, loyer, description,
                                   nb_pieces, surface, meuble, contact_bailleur, telephone_bailleur, proposition_id)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        ''', (titre,
              request.form.get('type_logement', ''),
              request.form.get('quartier', ''),
              request.form.get('ville', 'Agadez'),
              request.form.get('loyer', ''),
              request.form.get('description', ''),
              request.form.get('nb_pieces', ''),
              request.form.get('surface', ''),
              1 if request.form.get('meuble') == '1' else 0,
              request.form.get('contact_bailleur', ''),
              request.form.get('telephone_bailleur', ''),
              request.form.get('proposition_id') or None))
        log_id = cursor.lastrowid
        est_premier = True
        for fichier in request.files.getlist('fichiers')[:10]:
            nom_f, type_f = sauvegarder_fichier(fichier)
            if nom_f:
                conn.execute('INSERT INTO logement_photos (logement_id, nom_fichier, type_fichier, est_principale) VALUES (?,?,?,?)',
                             (log_id, nom_f, type_f, 1 if est_premier else 0))
                est_premier = False
        # Marquer la proposition comme publiee
        prop_id = request.form.get('proposition_id')
        if prop_id:
            conn.execute("UPDATE propositions SET statut='publie' WHERE id=?", (prop_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        print(f"[ERREUR publier logement] {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin/api/logement/<int:id>/disponible', methods=['POST'])
def admin_toggle_disponible(id):
    if not session.get('admin'): return jsonify({'success': False}), 401
    data = request.get_json()
    conn = get_db()
    conn.execute('UPDATE logements SET disponible=? WHERE id=?', (data.get('disponible', 1), id))
    conn.commit(); conn.close()
    return jsonify({'success': True})

@app.route('/admin/api/logement/<int:id>', methods=['DELETE'])
def admin_supprimer_logement(id):
    if not session.get('admin'): return jsonify({'success': False}), 401
    conn = get_db()
    photos = conn.execute('SELECT nom_fichier FROM logement_photos WHERE logement_id=?', (id,)).fetchall()
    for p in photos:
        chemin = os.path.join(Config.UPLOAD_FOLDER, p['nom_fichier'])
        if os.path.exists(chemin): os.remove(chemin)
    conn.execute('DELETE FROM logement_photos WHERE logement_id=?', (id,))
    conn.execute('DELETE FROM logements WHERE id=?', (id,))
    conn.commit(); conn.close()
    return jsonify({'success': True})

@app.route('/admin/api/proposition/<int:id>/data')
def admin_get_proposition_data(id):
    if not session.get('admin'): return jsonify({'success': False}), 401
    conn = get_db()
    p = conn.execute('SELECT * FROM propositions WHERE id=?', (id,)).fetchone()
    conn.close()
    if not p: return jsonify({'success': False})
    return jsonify({'success': True, 'data': {
        'id': p['id'], 'nom': p['nom'], 'telephone': p['telephone'],
        'type': p['type_logement'], 'quartier': p['quartier'],
        'loyer': p['loyer'], 'description': p['description']
    }})

# --- ADMIN : ACTIONS DEMANDES / PROPOSITIONS ------------------------------------

@app.route('/admin/api/demande/<int:id>/statut', methods=['POST'])
def admin_statut_demande(id):
    if not session.get('admin'): return jsonify({'success': False}), 401
    conn = get_db()
    conn.execute('UPDATE demandes SET statut=? WHERE id=?', (request.get_json().get('statut'), id))
    conn.commit(); conn.close()
    return jsonify({'success': True})

@app.route('/admin/api/demande/<int:id>', methods=['DELETE'])
def admin_supprimer_demande(id):
    if not session.get('admin'): return jsonify({'success': False}), 401
    conn = get_db(); conn.execute('DELETE FROM demandes WHERE id=?', (id,)); conn.commit(); conn.close()
    return jsonify({'success': True})

@app.route('/admin/api/proposition/<int:id>/statut', methods=['POST'])
def admin_statut_proposition(id):
    if not session.get('admin'): return jsonify({'success': False}), 401
    conn = get_db()
    conn.execute('UPDATE propositions SET statut=? WHERE id=?', (request.get_json().get('statut'), id))
    conn.commit(); conn.close()
    return jsonify({'success': True})

@app.route('/admin/api/proposition/<int:id>', methods=['DELETE'])
def admin_supprimer_proposition(id):
    if not session.get('admin'): return jsonify({'success': False}), 401
    conn = get_db()
    for f in conn.execute('SELECT nom_fichier FROM fichiers WHERE proposition_id=?', (id,)).fetchall():
        chemin = os.path.join(Config.UPLOAD_FOLDER, f['nom_fichier'])
        if os.path.exists(chemin): os.remove(chemin)
    conn.execute('DELETE FROM fichiers WHERE proposition_id=?', (id,))
    conn.execute('DELETE FROM propositions WHERE id=?', (id,))
    conn.commit(); conn.close()
    return jsonify({'success': True})

# --- ADMIN : VOIR FICHIERS -------------------------------------------------------

# fichiers -> templates/fichiers.html

@app.route('/admin/fichiers/<int:prop_id>')
def admin_fichiers(prop_id):
    if not session.get('admin'): return redirect(url_for('admin_login'))
    conn = get_db()
    p = conn.execute('SELECT nom FROM propositions WHERE id=?', (prop_id,)).fetchone()
    fichiers = conn.execute('SELECT * FROM fichiers WHERE proposition_id=?', (prop_id,)).fetchall()
    conn.close()
    return render_template("fichiers.html", fichiers=fichiers,
                                  title=f"Fichiers proposition #{prop_id} - {p['nom'] if p else ''}")

@app.route('/admin/fichiers-logement/<int:log_id>')
def admin_fichiers_logement(log_id):
    if not session.get('admin'): return redirect(url_for('admin_login'))
    conn = get_db()
    l = conn.execute('SELECT titre FROM logements WHERE id=?', (log_id,)).fetchone()
    fichiers = conn.execute('SELECT * FROM logement_photos WHERE logement_id=?', (log_id,)).fetchall()
    conn.close()
    return render_template("fichiers.html", fichiers=fichiers,
                                  title=f"Photos logement #{log_id} - {l['titre'] if l else ''}")

# --- DEMARRAGE -------------------------------------------------------------------

if __name__ == '__main__':
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    init_db()
    print("=" * 52)
    print("  Loge Facile Niger - Serveur demarre")
    print("  Site  : http://localhost:5000")
    print("  Admin : http://localhost:5000/admin")
    print("=" * 52)
    app.run(debug=True, host='0.0.0.0', port=5000)
