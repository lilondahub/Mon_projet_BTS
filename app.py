from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

# Connexion à la base de données
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="2Gjfzres@78000p02",
        database="inventaire"
    )

@app.route('/', methods=['GET', 'POST'])
def index():
    infos_systeme = []
    infos_contact = []
    error_message = ""
    
    if request.method == 'POST':
        search_type = request.form.get('search_type')
        search_value = request.form.get('search_value')

        if search_type and search_value:
            try:
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)

                # Récupère l'asset_tag associé à la recherche
                query = f"SELECT asset_tag FROM asset WHERE {search_type} = %s"
                cursor.execute(query, (search_value,))
                rows = cursor.fetchall()

                if rows:
                    for row in rows:
                        asset_tag = row['asset_tag']

                        # Infos système
                        cursor.execute("""
                            SELECT asset_tag, sn, ip, operating_system AS os
                            FROM asset WHERE asset_tag = %s
                        """, (asset_tag,))
                        infos_systeme.extend(cursor.fetchall())

                        # Infos contact
                        cursor.execute("""
                            SELECT asset_tag, department, contact, location, responsable
                            FROM contact WHERE asset_tag = %s
                        """, (asset_tag,))
                        infos_contact.extend(cursor.fetchall())
                else:
                    error_message = "Aucun résultat trouvé. Vérifiez votre saisie."

                cursor.close()
                conn.close()
            except Exception as e:
                error_message = "Erreur lors de la recherche."

    return render_template('index.html',
                           infos_systeme=infos_systeme,
                           infos_contact=infos_contact,
                           error_message=error_message)

if __name__ == '__main__':
    app.run(debug=True)
