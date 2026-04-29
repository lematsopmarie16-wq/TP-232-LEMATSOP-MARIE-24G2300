import json
import os
import math
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import csv
import io
import os

app = Flask(__name__)
CORS(app)

DATA_FILE = "etudiants.json"

# ---------- Chargement / Sauvegarde ----------
def load_etudiants():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []

def save_etudiants(etudiants):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(etudiants, f, indent=2, ensure_ascii=False)

# ---------- Utilitaires statistiques (sans numpy) ----------
def compute_stats(values):
    if not values:
        return {}
    values_sorted = sorted(values)
    n = len(values)
    mean = sum(values) / n
    # Variance et écart-type
    variance = sum((x - mean) ** 2 for x in values) / n
    std = math.sqrt(variance)
    # Quartiles
    q1 = values_sorted[int(0.25 * n)] if n >= 4 else values_sorted[0]
    q2 = values_sorted[int(0.50 * n)] if n >= 2 else values_sorted[0]
    q3 = values_sorted[int(0.75 * n)] if n >= 4 else values_sorted[-1]
    return {
        "count": n,
        "moyenne": round(mean, 2),
        "ecart_type": round(std, 2),
        "minimum": round(min(values), 2),
        "maximum": round(max(values), 2),
        "Q1": round(q1, 2),
        "Q2": round(q2, 2),
        "Q3": round(q3, 2)
    }

def pearson_corr(x, y):
    """Calcul de corrélation de Pearson sans numpy"""
    n = len(x)
    if n < 2:
        return 0
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    
    num = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    den_x = math.sqrt(sum((xi - mean_x) ** 2 for xi in x))
    den_y = math.sqrt(sum((yi - mean_y) ** 2 for yi in y))
    
    if den_x == 0 or den_y == 0:
        return 0
    return round(num / (den_x * den_y), 4)

# ---------- Initialisation avec 20 données ----------
def init_data():
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        initial_data = [
            {"id": 1, "nom": "Emma Laurent", "age": 20, "sexe": "F", "ville": "Paris", "niveau": "L3", "boursier": True,
             "revenus_mensuels": 850, "depenses_total": 820, "logement": 450, "alimentation": 180, 
             "transports": 50, "loisirs": 70, "etudes": 40, "autres": 30, "economies": 30,
             "categorie_depense_principale": "logement", "date_enregistrement": "2026-01-15T08:30:00"},
            {"id": 2, "nom": "Thomas Mercier", "age": 22, "sexe": "M", "ville": "Lyon", "niveau": "M1", "boursier": False,
             "revenus_mensuels": 1200, "depenses_total": 1150, "logement": 500, "alimentation": 250,
             "transports": 80, "loisirs": 150, "etudes": 100, "autres": 70, "economies": 50,
             "categorie_depense_principale": "loisirs", "date_enregistrement": "2026-02-20T10:15:00"},
            {"id": 3, "nom": "Sophie Dubois", "age": 19, "sexe": "F", "ville": "Marseille", "niveau": "L2", "boursier": True,
             "revenus_mensuels": 750, "depenses_total": 740, "logement": 400, "alimentation": 160,
             "transports": 40, "loisirs": 60, "etudes": 50, "autres": 30, "economies": 10,
             "categorie_depense_principale": "logement", "date_enregistrement": "2026-03-10T14:45:00"},
            {"id": 4, "nom": "Lucas Rivière", "age": 23, "sexe": "M", "ville": "Toulouse", "niveau": "M2", "boursier": False,
             "revenus_mensuels": 1500, "depenses_total": 1400, "logement": 600, "alimentation": 300,
             "transports": 100, "loisirs": 200, "etudes": 120, "autres": 80, "economies": 100,
             "categorie_depense_principale": "loisirs", "date_enregistrement": "2026-04-05T09:00:00"},
            {"id": 5, "nom": "Chloé Bernard", "age": 20, "sexe": "F", "ville": "Nice", "niveau": "L3", "boursier": True,
             "revenus_mensuels": 800, "depenses_total": 780, "logement": 420, "alimentation": 170,
             "transports": 45, "loisirs": 80, "etudes": 45, "autres": 20, "economies": 20,
             "categorie_depense_principale": "logement", "date_enregistrement": "2026-05-12T11:30:00"},
            {"id": 6, "nom": "Hugo Petit", "age": 21, "sexe": "M", "ville": "Bordeaux", "niveau": "L3", "boursier": False,
             "revenus_mensuels": 1100, "depenses_total": 1050, "logement": 480, "alimentation": 220,
             "transports": 60, "loisirs": 130, "etudes": 80, "autres": 80, "economies": 50,
             "categorie_depense_principale": "loisirs", "date_enregistrement": "2026-06-18T16:00:00"},
            {"id": 7, "nom": "Julie Vincent", "age": 20, "sexe": "F", "ville": "Strasbourg", "niveau": "L2", "boursier": True,
             "revenus_mensuels": 820, "depenses_total": 800, "logement": 440, "alimentation": 175,
             "transports": 55, "loisirs": 65, "etudes": 45, "autres": 20, "economies": 20,
             "categorie_depense_principale": "logement", "date_enregistrement": "2026-07-22T13:15:00"},
            {"id": 8, "nom": "Antoine Girard", "age": 24, "sexe": "M", "ville": "Nantes", "niveau": "M2", "boursier": False,
             "revenus_mensuels": 1600, "depenses_total": 1480, "logement": 650, "alimentation": 320,
             "transports": 90, "loisirs": 220, "etudes": 110, "autres": 90, "economies": 120,
             "categorie_depense_principale": "loisirs", "date_enregistrement": "2026-08-30T08:45:00"},
            {"id": 9, "nom": "Camille Nguyen", "age": 19, "sexe": "F", "ville": "Lille", "niveau": "L1", "boursier": True,
             "revenus_mensuels": 780, "depenses_total": 760, "logement": 410, "alimentation": 165,
             "transports": 50, "loisirs": 70, "etudes": 45, "autres": 20, "economies": 20,
             "categorie_depense_principale": "logement", "date_enregistrement": "2026-09-14T10:30:00"},
            {"id": 10, "nom": "Maxime Thomas", "age": 22, "sexe": "M", "ville": "Rennes", "niveau": "M1", "boursier": False,
             "revenus_mensuels": 1300, "depenses_total": 1250, "logement": 520, "alimentation": 260,
             "transports": 70, "loisirs": 180, "etudes": 90, "autres": 130, "economies": 50,
             "categorie_depense_principale": "loisirs", "date_enregistrement": "2026-10-20T15:00:00"},
            {"id": 11, "nom": "Léa Simon", "age": 18, "sexe": "F", "ville": "Montpellier", "niveau": "L1", "boursier": True,
             "revenus_mensuels": 720, "depenses_total": 710, "logement": 380, "alimentation": 155,
             "transports": 45, "loisirs": 60, "etudes": 40, "autres": 30, "economies": 10,
             "categorie_depense_principale": "logement", "date_enregistrement": "2026-11-25T07:00:00"},
            {"id": 12, "nom": "Nicolas Fournier", "age": 21, "sexe": "M", "ville": "Grenoble", "niveau": "L3", "boursier": False,
             "revenus_mensuels": 1150, "depenses_total": 1100, "logement": 490, "alimentation": 230,
             "transports": 65, "loisirs": 140, "etudes": 85, "autres": 90, "economies": 50,
             "categorie_depense_principale": "loisirs", "date_enregistrement": "2026-12-05T12:00:00"},
            {"id": 13, "nom": "Manon Charpentier", "age": 22, "sexe": "F", "ville": "Dijon", "niveau": "M1", "boursier": True,
             "revenus_mensuels": 880, "depenses_total": 850, "logement": 460, "alimentation": 190,
             "transports": 50, "loisirs": 85, "etudes": 45, "autres": 20, "economies": 30,
             "categorie_depense_principale": "logement", "date_enregistrement": "2027-01-18T09:30:00"},
            {"id": 14, "nom": "Baptiste Leroy", "age": 23, "sexe": "M", "ville": "Aix-en-Provence", "niveau": "M2", "boursier": False,
             "revenus_mensuels": 1450, "depenses_total": 1380, "logement": 580, "alimentation": 290,
             "transports": 85, "loisirs": 210, "etudes": 105, "autres": 110, "economies": 70,
             "categorie_depense_principale": "loisirs", "date_enregistrement": "2027-02-22T14:15:00"},
            {"id": 15, "nom": "Inès Moreau", "age": 20, "sexe": "F", "ville": "Saint-Étienne", "niveau": "L2", "boursier": True,
             "revenus_mensuels": 800, "depenses_total": 785, "logement": 430, "alimentation": 175,
             "transports": 45, "loisirs": 75, "etudes": 40, "autres": 20, "economies": 15,
             "categorie_depense_principale": "logement", "date_enregistrement": "2027-03-15T11:00:00"},
            {"id": 16, "nom": "Romain Blanc", "age": 21, "sexe": "M", "ville": "Nancy", "niveau": "L3", "boursier": False,
             "revenus_mensuels": 1080, "depenses_total": 1020, "logement": 470, "alimentation": 210,
             "transports": 55, "loisirs": 125, "etudes": 80, "autres": 80, "economies": 60,
             "categorie_depense_principale": "loisirs", "date_enregistrement": "2027-04-10T09:00:00"},
            {"id": 17, "nom": "Sarah Kone", "age": 19, "sexe": "F", "ville": "Tours", "niveau": "L2", "boursier": True,
             "revenus_mensuels": 760, "depenses_total": 745, "logement": 395, "alimentation": 165,
             "transports": 40, "loisirs": 70, "etudes": 45, "autres": 30, "economies": 15,
             "categorie_depense_principale": "logement", "date_enregistrement": "2027-05-20T14:00:00"},
            {"id": 18, "nom": "Alexis Perrin", "age": 24, "sexe": "M", "ville": "Angers", "niveau": "M2", "boursier": False,
             "revenus_mensuels": 1700, "depenses_total": 1550, "logement": 700, "alimentation": 340,
             "transports": 95, "loisirs": 240, "etudes": 100, "autres": 75, "economies": 150,
             "categorie_depense_principale": "loisirs", "date_enregistrement": "2027-06-25T11:30:00"},
            {"id": 19, "nom": "Laura Robert", "age": 22, "sexe": "F", "ville": "Reims", "niveau": "M1", "boursier": True,
             "revenus_mensuels": 860, "depenses_total": 830, "logement": 445, "alimentation": 180,
             "transports": 45, "loisirs": 80, "etudes": 50, "autres": 30, "economies": 30,
             "categorie_depense_principale": "logement", "date_enregistrement": "2027-07-30T16:00:00"},
            {"id": 20, "nom": "Jérémy Dubois", "age": 21, "sexe": "M", "ville": "Clermont-Ferrand", "niveau": "L3", "boursier": False,
             "revenus_mensuels": 1120, "depenses_total": 1080, "logement": 490, "alimentation": 225,
             "transports": 60, "loisirs": 145, "etudes": 80, "autres": 80, "economies": 40,
             "categorie_depense_principale": "loisirs", "date_enregistrement": "2027-08-15T10:00:00"}
        ]
        save_etudiants(initial_data)

# ---------- Routes API ----------
@app.route("/api/etudiants", methods=["GET"])
def get_etudiants():
    etudiants = load_etudiants()
    return jsonify(etudiants)

@app.route("/api/etudiants", methods=["POST"])
def add_etudiant():
    data = request.json
    required = ["nom", "age", "sexe", "revenus_mensuels", "logement", "alimentation", "transports", "loisirs", "etudes", "autres"]
    for field in required:
        if not data.get(field) and data.get(field) != 0:
            return jsonify({"error": f"Le champ {field} est obligatoire"}), 400

    etudiants = load_etudiants()
    new_id = max([e["id"] for e in etudiants], default=0) + 1

    depenses_total = (
        float(data.get("logement", 0)) +
        float(data.get("alimentation", 0)) +
        float(data.get("transports", 0)) +
        float(data.get("loisirs", 0)) +
        float(data.get("etudes", 0)) +
        float(data.get("autres", 0))
    )
    
    revenus = float(data["revenus_mensuels"])
    economies = round(revenus - depenses_total, 2)
    
    categories = {
        "logement": float(data.get("logement", 0)),
        "alimentation": float(data.get("alimentation", 0)),
        "loisirs": float(data.get("loisirs", 0)),
        "transports": float(data.get("transports", 0)),
        "etudes": float(data.get("etudes", 0)),
        "autres": float(data.get("autres", 0))
    }
    categorie_principale = max(categories, key=categories.get)
    ratio_depenses_revenus = round((depenses_total / revenus) * 100, 1) if revenus > 0 else None

    etudiant = {
        "id": new_id,
        "nom": data["nom"],
        "age": int(data["age"]),
        "sexe": data["sexe"],
        "ville": data.get("ville", ""),
        "niveau": data.get("niveau", ""),
        "boursier": data.get("boursier", False),
        "revenus_mensuels": revenus,
        "depenses_total": round(depenses_total, 2),
        "logement": round(float(data["logement"]), 2),
        "alimentation": round(float(data["alimentation"]), 2),
        "transports": round(float(data["transports"]), 2),
        "loisirs": round(float(data["loisirs"]), 2),
        "etudes": round(float(data["etudes"]), 2),
        "autres": round(float(data["autres"]), 2),
        "economies": economies,
        "categorie_depense_principale": categorie_principale,
        "ratio_depenses_revenus": ratio_depenses_revenus,
        "date_enregistrement": datetime.now().isoformat()
    }
    etudiants.append(etudiant)
    save_etudiants(etudiants)
    return jsonify({"message": "Étudiant ajouté", "id": new_id, "economies": economies}), 201

@app.route("/api/stats/descriptives", methods=["GET"])
def stats_descriptives():
    etudiants = load_etudiants()
    if not etudiants:
        return jsonify({"total": 0, "message": "Aucune donnée"})

    ages = [e["age"] for e in etudiants if e.get("age")]
    revenus = [e["revenus_mensuels"] for e in etudiants if e.get("revenus_mensuels")]
    depenses = [e["depenses_total"] for e in etudiants if e.get("depenses_total")]
    logement = [e["logement"] for e in etudiants if e.get("logement")]
    alimentation = [e["alimentation"] for e in etudiants if e.get("alimentation")]
    loisirs = [e["loisirs"] for e in etudiants if e.get("loisirs")]
    transports = [e["transports"] for e in etudiants if e.get("transports")]
    etudes = [e["etudes"] for e in etudiants if e.get("etudes")]
    autres = [e["autres"] for e in etudiants if e.get("autres")]
    economies = [e["economies"] for e in etudiants if e.get("economies") is not None]
    ratios = [e["ratio_depenses_revenus"] for e in etudiants if e.get("ratio_depenses_revenus")]

    hommes = [e for e in etudiants if e.get("sexe") == "M"]
    femmes = [e for e in etudiants if e.get("sexe") == "F"]
    
    niveaux = {}
    for niveau in ["L1", "L2", "L3", "M1", "M2"]:
        etud_niveau = [e for e in etudiants if e.get("niveau") == niveau]
        niveaux[niveau] = {
            "count": len(etud_niveau),
            "depenses_moyennes": round(sum(e["depenses_total"] for e in etud_niveau) / len(etud_niveau), 2) if etud_niveau else 0,
            "revenus_moyens": round(sum(e["revenus_mensuels"] for e in etud_niveau) / len(etud_niveau), 2) if etud_niveau else 0
        }

    boursiers = [e for e in etudiants if e.get("boursier") is True]
    non_boursiers = [e for e in etudiants if e.get("boursier") is False]

    result = {
        "total": len(etudiants),
        "age": compute_stats(ages),
        "revenus_mensuels": compute_stats(revenus),
        "depenses_total": compute_stats(depenses),
        "logement": compute_stats(logement),
        "alimentation": compute_stats(alimentation),
        "loisirs": compute_stats(loisirs),
        "transports": compute_stats(transports),
        "etudes": compute_stats(etudes),
        "autres": compute_stats(autres),
        "economies": compute_stats(economies),
        "ratio_depenses_revenus": compute_stats(ratios),
        "par_sexe": {
            "hommes": {
                "count": len(hommes),
                "depenses_moyennes": round(sum(e["depenses_total"] for e in hommes) / len(hommes), 2) if hommes else 0,
                "revenus_moyens": round(sum(e["revenus_mensuels"] for e in hommes) / len(hommes), 2) if hommes else 0
            },
            "femmes": {
                "count": len(femmes),
                "depenses_moyennes": round(sum(e["depenses_total"] for e in femmes) / len(femmes), 2) if femmes else 0,
                "revenus_moyens": round(sum(e["revenus_mensuels"] for e in femmes) / len(femmes), 2) if femmes else 0
            }
        },
        "par_niveau": niveaux,
        "par_bourse": {
            "boursiers": {"count": len(boursiers), "depenses_moyennes": round(sum(e["depenses_total"] for e in boursiers) / len(boursiers), 2) if boursiers else 0},
            "non_boursiers": {"count": len(non_boursiers), "depenses_moyennes": round(sum(e["depenses_total"] for e in non_boursiers) / len(non_boursiers), 2) if non_boursiers else 0}
        }
    }
    return jsonify(result)

@app.route("/api/correlation", methods=["GET"])
def correlation_matrix():
    etudiants = load_etudiants()
    if len(etudiants) < 3:
        return jsonify({"error": "Pas assez de données pour la matrice de corrélation"})

    variables = ["revenus_mensuels", "depenses_total", "logement", "alimentation", "loisirs", "transports", "etudes"]
    filtered = []
    for e in etudiants:
        if all(e.get(v) is not None for v in variables):
            filtered.append(e)
    if len(filtered) < 3:
        return jsonify({"error": "Données insuffisantes pour la corrélation"})

    data = {v: [e[v] for e in filtered] for v in variables}
    matrix = []
    for v1 in variables:
        row = []
        for v2 in variables:
            corr = pearson_corr(data[v1], data[v2])
            row.append(corr)
        matrix.append(row)
    return jsonify({"variables": variables, "matrix": matrix})

@app.route("/api/export/csv", methods=["GET"])
def export_csv():
    etudiants = load_etudiants()
    if not etudiants:
        return "Aucune donnée à exporter", 404

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "nom", "age", "sexe", "ville", "niveau", "boursier", "revenus_mensuels",
                     "depenses_total", "logement", "alimentation", "transports", "loisirs", "etudes", 
                     "autres", "economies", "categorie_depense_principale", "ratio_depenses_revenus", "date_enregistrement"])
    for e in etudiants:
        writer.writerow([
            e.get("id", ""), e.get("nom", ""), e.get("age", ""), e.get("sexe", ""),
            e.get("ville", ""), e.get("niveau", ""), e.get("boursier", ""), e.get("revenus_mensuels", ""),
            e.get("depenses_total", ""), e.get("logement", ""), e.get("alimentation", ""),
            e.get("transports", ""), e.get("loisirs", ""), e.get("etudes", ""),
            e.get("autres", ""), e.get("economies", ""), e.get("categorie_depense_principale", ""),
            e.get("ratio_depenses_revenus", ""), e.get("date_enregistrement", "")
        ])
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='export_depenses_etudiants.csv'
    )

@app.route("/")
def serve_frontend():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Le fichier index.html n'est pas présent.", 200


if __name__ == "__main__":
    init_data()
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
