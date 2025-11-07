import graphene
import requests
from ml.model import predecir_paciente, entrenar_modelo_con_datos, TriajeML
from db.connection import SessionLocal
from ml.clustering import entrenar_clusters, predecir_cluster, agrupar_pacientes


# --- QUERIES ---
class BaseQuery(graphene.ObjectType):
    hello = graphene.String(default_value="✅ Microservicio ML operativo y conectado a la base de datos")


# --- MUTATIONS ---
class SincronizarTriajes(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info):
        try:
            graphql_query = {
                "query": """
                {
                    triajes {
                        id
                        temperatura
                        peso
                        estatura
                        frecuenciaCardiaca
                        frecuenciaRespiratoria
                        saturacionOxigeno
                        alergias
                        enfermedadesCronicas
                        motivoConsulta
                    }
                }
                """
            }

            response = requests.post("http://localhost:8080/graphql", json=graphql_query)
            data = response.json()["data"]["triajes"]

            if not data:
                return SincronizarTriajes(ok=False, message="⚠️ No se encontraron triajes en el backend")

            db = SessionLocal()

            for triaje in data:
                # --- Evitar duplicados ---
                exists = db.query(TriajeML).filter_by(id_triaje=triaje["id"]).first()
                if exists:
                    continue

                # --- Predicción ML ---
                datos_paciente = {
                    "temperatura": triaje["temperatura"],
                    "frecuencia_cardiaca": triaje["frecuenciaCardiaca"],
                    "frecuencia_respiratoria": triaje["frecuenciaRespiratoria"],
                    "saturacion_oxigeno": triaje["saturacionOxigeno"],
                    "peso": triaje["peso"],
                    "estatura": triaje["estatura"],
                }

                resultado = predecir_paciente(datos_paciente)

                # --- Insertar nuevo registro ---
                nuevo_triaje = TriajeML(
                    id_triaje=triaje["id"],  # 👈 guardamos el ID del backend original
                    nombre_paciente=f"Paciente_{triaje['id']}",
                    temperatura=triaje["temperatura"],
                    frecuencia_cardiaca=triaje["frecuenciaCardiaca"],
                    frecuencia_respiratoria=triaje["frecuenciaRespiratoria"],
                    saturacion_oxigeno=triaje["saturacionOxigeno"],
                    peso=triaje["peso"],
                    estatura=triaje["estatura"],
                    alergias=triaje["alergias"],
                    enfermedades_cronicas=triaje["enfermedadesCronicas"],
                    motivo_consulta=triaje["motivoConsulta"],
                    sufre_infarto=resultado["sufre_infarto"]
                )

                db.add(nuevo_triaje)

            db.commit()
            db.close()

            return SincronizarTriajes(ok=True, message=f"✅ {len(data)} triajes sincronizados e insertados correctamente.")

        except Exception as e:
            return SincronizarTriajes(ok=False, message=f"❌ Error al sincronizar: {str(e)}")


class ObtenerTriajesRiesgo(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()
    triajes = graphene.List(graphene.JSONString)

    def mutate(self, info):
        try:
            db = SessionLocal()
            triajes_riesgo = db.query(TriajeML).filter(TriajeML.sufre_infarto == True).all()

            if not triajes_riesgo:
                return ObtenerTriajesRiesgo(ok=True, message="⚠️ No hay pacientes con riesgo de infarto.", triajes=[])

            lista_triajes = [
                {
                    "id_triaje": t.id_triaje,
                    "nombre_paciente": t.nombre_paciente,
                    "temperatura": t.temperatura,
                    "frecuencia_cardiaca": t.frecuencia_cardiaca,
                    "frecuencia_respiratoria": t.frecuencia_respiratoria,
                    "saturacion_oxigeno": t.saturacion_oxigeno,
                    "peso": t.peso,
                    "estatura": t.estatura,
                    "alergias": t.alergias,
                    "enfermedades_cronicas": t.enfermedades_cronicas,
                    "motivo_consulta": t.motivo_consulta,
                    "sufre_infarto": t.sufre_infarto
                }
                for t in triajes_riesgo
            ]

            db.close()
            return ObtenerTriajesRiesgo(ok=True, message="✅ Pacientes con riesgo de infarto encontrados.", triajes=lista_triajes)

        except Exception as e:
            return ObtenerTriajesRiesgo(ok=False, message=f"❌ Error al consultar triajes: {str(e)}", triajes=[])


class EntrenarModelo(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info):
        try:
            resultado = entrenar_modelo_con_datos()
            return EntrenarModelo(ok=True, message=f"✅ {resultado}")
        except Exception as e:
            return EntrenarModelo(ok=False, message=f"❌ Error al entrenar: {str(e)}")


class EntrenarClusters(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        num_clusters = graphene.Int(required=False, default_value=3)

    def mutate(self, info, num_clusters):
        try:
            resultado = entrenar_clusters(num_clusters)
            return EntrenarClusters(ok=True, message=resultado)
        except Exception as e:
            return EntrenarClusters(ok=False, message=f"❌ Error al entrenar clusters: {str(e)}")


class PredecirCluster(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()
    cluster = graphene.Int()

    class Arguments:
        temperatura = graphene.Float(required=True)
        frecuencia_cardiaca = graphene.Float(required=True)
        frecuencia_respiratoria = graphene.Float(required=True)
        saturacion_oxigeno = graphene.Float(required=True)
        peso = graphene.Float(required=True)
        estatura = graphene.Float(required=True)

    def mutate(self, info, temperatura, frecuencia_cardiaca, frecuencia_respiratoria, saturacion_oxigeno, peso, estatura):
        try:
            datos = {
                "temperatura": temperatura,
                "frecuencia_cardiaca": frecuencia_cardiaca,
                "frecuencia_respiratoria": frecuencia_respiratoria,
                "saturacion_oxigeno": saturacion_oxigeno,
                "peso": peso,
                "estatura": estatura
            }
            resultado = predecir_cluster(datos)
            return PredecirCluster(ok=True, message=resultado["mensaje"], cluster=resultado["cluster"])
        except Exception as e:
            return PredecirCluster(ok=False, message=f"❌ Error al predecir cluster: {str(e)}", cluster=-1)


# --- NUEVA QUERY PARA VER TODOS LOS CLUSTERS ---
class PacienteCluster(graphene.ObjectType):
    id_triaje = graphene.Int()
    cluster = graphene.Int()


class Query(BaseQuery):  # 👈 Extiende la Query original sin eliminar 'hello'
    obtener_clusters = graphene.List(PacienteCluster)

    def resolve_obtener_clusters(self, info):
        print("🔍 Ejecutando obtener_clusters...")
        resultado = agrupar_pacientes()
        print("Resultado:", resultado)  # 👈 Muestra lo que devuelve

        if not resultado:
            print("⚠️ agrupar_pacientes devolvió vacío o None")
            return []
        return [PacienteCluster(id_triaje=r["id_triaje"], cluster=r["cluster"]) for r in resultado]

# --- SCHEMA GLOBAL ---
class Mutation(graphene.ObjectType):
    sincronizar_triajes = SincronizarTriajes.Field()
    obtener_triajes_riesgo = ObtenerTriajesRiesgo.Field()
    entrenar_modelo = EntrenarModelo.Field()
    entrenar_clusters = EntrenarClusters.Field()
    predecir_cluster = PredecirCluster.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
