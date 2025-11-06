import graphene
import requests
from ml.model import predecir_paciente, entrenar_modelo_con_datos, TriajeML
from db.connection import SessionLocal

# --- QUERIES ---
class Query(graphene.ObjectType):
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
                    "id_triaje": t.id_triaje,  # cambiamos aquí
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


# --- SCHEMA GLOBAL ---
class Mutation(graphene.ObjectType):
    sincronizar_triajes = SincronizarTriajes.Field()
    obtener_triajes_riesgo = ObtenerTriajesRiesgo.Field()
    entrenar_modelo = EntrenarModelo.Field()
