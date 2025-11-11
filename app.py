from flask import Flask, request, jsonify, render_template_string
from graphene import Schema
from schema import Query, Mutation
import os
from dotenv import load_dotenv
from db.connection import init_db  # Agregado
from flask_cors import CORS  # ✅ Importar CORS

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# ✅ Habilitar CORS para permitir solicitudes desde Angular (puedes ajustar la URL)
CORS(app, resources={r"/graphql": {"origins": "http://localhost:4200"}})

# Crear el esquema de GraphQL
schema = Schema(query=Query, mutation=Mutation)

# HTML simple para usar GraphiQL (interfaz web)
GRAPHIQL_TEMPLATE = """
<!DOCTYPE html>
<html>
  <head>
    <title>GraphiQL</title>
    <link rel="stylesheet" href="//unpkg.com/graphiql/graphiql.min.css" />
  </head>
  <body style="margin: 0;">
    <div id="graphiql" style="height: 100vh;"></div>
    <script crossorigin src="//unpkg.com/react/umd/react.production.min.js"></script>
    <script crossorigin src="//unpkg.com/react-dom/umd/react-dom.production.min.js"></script>
    <script crossorigin src="//unpkg.com/graphiql/graphiql.min.js"></script>
    <script>
      const graphQLFetcher = graphQLParams =>
        fetch('/graphql', {
          method: 'post',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(graphQLParams),
        })
        .then(response => response.json())
        .catch(() => response.text());
      ReactDOM.render(
        React.createElement(GraphiQL, { fetcher: graphQLFetcher }),
        document.getElementById('graphiql'),
      );
    </script>
  </body>
</html>
"""

@app.route("/graphql", methods=["GET"])
def graphiql_view():
    return render_template_string(GRAPHIQL_TEMPLATE)

@app.route("/graphql", methods=["POST"])
def graphql_api():
    data = request.get_json()
    result = schema.execute(
        data.get("query"),
        variables=data.get("variables")
    )

    response = {}
    if result.errors:
        print("❌ Errores en GraphQL:", result.errors)
        response["errors"] = [str(e) for e in result.errors]

    response["data"] = result.data
    return jsonify(response)

from apscheduler.schedulers.background import BackgroundScheduler
from ml.model import entrenar_modelo_con_datos

def entrenar_modelo_diariamente():
    print("🧠 Entrenando modelo automáticamente...")
    try:
        resultado = entrenar_modelo_con_datos()
        print(f"✅ Entrenamiento completado automáticamente: {resultado}")
    except Exception as e:
        print(f"❌ Error durante el entrenamiento automático: {str(e)}")

scheduler = BackgroundScheduler()
scheduler.add_job(entrenar_modelo_diariamente, 'cron', hour=2, minute=0)
scheduler.start()

if __name__ == "__main__":
    init_db()
    port = int(os.getenv("PORT", 5000))
    print(f"🚀 Servidor ML corriendo en http://localhost:{port}/graphql")
    app.run(debug=True, port=port)
