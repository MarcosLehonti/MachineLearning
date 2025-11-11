import graphene
import requests
from ml.model import predecir_paciente, entrenar_modelo_con_datos, TriajeML
from db.connection import SessionLocal
from ml.clustering import entrenar_clusters, predecir_cluster, agrupar_pacientes
from ml.ecg_model import analizar_ecg_mock, obtener_historico_ecg_mock, entrenar_modelo_ecg_mock


# --- QUERIES ---
class BaseQuery(graphene.ObjectType):
    hello = graphene.String(default_value="Microservicio ML operativo y conectado a la base de datos")


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

            response = requests.post("https://backend-historialclinico-sofware2.onrender.com/graphql", json=graphql_query)
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
                    sufre_infarto=resultado["sufre_infarto"],
                )

                db.add(nuevo_triaje)

            db.commit()
            db.close()

            return SincronizarTriajes(
                ok=True, message=f"[OK] {len(data)} triajes sincronizados e insertados correctamente."
            )

        except Exception as e:
            return SincronizarTriajes(ok=False, message=f"[ERROR] Error al sincronizar: {str(e)}")


class ObtenerTriajesRiesgo(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()
    triajes = graphene.List(graphene.JSONString)

    def mutate(self, info):
        try:
            db = SessionLocal()
            triajes_riesgo = db.query(TriajeML).filter(TriajeML.sufre_infarto).all()

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
                    "sufre_infarto": t.sufre_infarto,
                }
                for t in triajes_riesgo
            ]

            db.close()
            return ObtenerTriajesRiesgo(
                ok=True, message="[OK] Pacientes con riesgo de infarto encontrados.", triajes=lista_triajes
            )

        except Exception as e:
            return ObtenerTriajesRiesgo(ok=False, message=f"[ERROR] Error al consultar triajes: {str(e)}", triajes=[])


class EntrenarModelo(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info):
        try:
            resultado = entrenar_modelo_con_datos()
            return EntrenarModelo(ok=True, message=f"[OK] {resultado}")
        except Exception as e:
            return EntrenarModelo(ok=False, message=f"[ERROR] Error al entrenar: {str(e)}")


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
            return EntrenarClusters(ok=False, message=f"[ERROR] Error al entrenar clusters: {str(e)}")


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

    def mutate(
        self, info, temperatura, frecuencia_cardiaca, frecuencia_respiratoria, saturacion_oxigeno, peso, estatura
    ):
        try:
            datos = {
                "temperatura": temperatura,
                "frecuencia_cardiaca": frecuencia_cardiaca,
                "frecuencia_respiratoria": frecuencia_respiratoria,
                "saturacion_oxigeno": saturacion_oxigeno,
                "peso": peso,
                "estatura": estatura,
            }
            resultado = predecir_cluster(datos)
            return PredecirCluster(ok=True, message=resultado["mensaje"], cluster=resultado["cluster"])
        except Exception as e:
            return PredecirCluster(ok=False, message=f"[ERROR] Error al predecir cluster: {str(e)}", cluster=-1)


# --- OBJETOS PARA ECG ---
class AnalisisECG(graphene.ObjectType):
    id_paciente = graphene.Int()
    archivo_imagen = graphene.String()
    fecha_analisis = graphene.String()
    diagnostico = graphene.String()
    descripcion = graphene.String()
    probabilidad = graphene.Int()
    nivel_riesgo = graphene.String()
    frecuencia_cardiaca = graphene.Int()
    estado = graphene.String()
    tiempo_procesamiento = graphene.String()
    modelo_utilizado = graphene.String()


class HistoricoECG(graphene.ObjectType):
    id_analisis = graphene.String()
    fecha_analisis = graphene.String()
    diagnostico = graphene.String()
    descripcion = graphene.String()
    probabilidad = graphene.Int()
    nivel_riesgo = graphene.String()
    archivo_imagen = graphene.String()


class EntrenarModeloECG(graphene.ObjectType):
    ok = graphene.Boolean()
    message = graphene.String()
    estado = graphene.String()
    precision = graphene.Float()
    dataset_size = graphene.Int()
    epocas = graphene.Int()
    tiempo_entrenamiento = graphene.String()
    modelo_version = graphene.String()


# --- NUEVA QUERY PARA VER TODOS LOS CLUSTERS ---
class PacienteCluster(graphene.ObjectType):
    id_triaje = graphene.Int()
    cluster = graphene.Int()


# --- MUTATIONS ECG ---
class AnalizarECGMutation(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()
    analisis = graphene.Field(AnalisisECG)

    class Arguments:
        archivo_imagen = graphene.String(required=True)
        id_paciente = graphene.Int(required=True)

    def mutate(self, info, archivo_imagen, id_paciente):
        try:
            resultado = analizar_ecg_mock(archivo_imagen, id_paciente)
            return AnalizarECGMutation(
                ok=True,
                message=f"[OK] Análisis ECG completado para paciente {id_paciente}",
                analisis=AnalisisECG(**resultado),
            )
        except Exception as e:
            return AnalizarECGMutation(ok=False, message=f"[ERROR] Error al analizar ECG: {str(e)}")


class ObtenerHistoricoECGMutation(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()
    historico = graphene.List(HistoricoECG)

    class Arguments:
        id_paciente = graphene.Int(required=True)

    def mutate(self, info, id_paciente):
        try:
            historico_data = obtener_historico_ecg_mock(id_paciente)
            historico = [HistoricoECG(**h) for h in historico_data]
            return ObtenerHistoricoECGMutation(
                ok=True, message=f"[OK] Historial ECG obtenido para paciente {id_paciente}", historico=historico
            )
        except Exception as e:
            return ObtenerHistoricoECGMutation(ok=False, message=f"[ERROR] Error al obtener historial: {str(e)}")


class EntrenarModeloECGMutation(graphene.Mutation):
    ok = graphene.Boolean()
    message = graphene.String()
    resultado = graphene.Field(EntrenarModeloECG)

    def mutate(self, info):
        try:
            resultado_data = entrenar_modelo_ecg_mock()
            return EntrenarModeloECGMutation(
                ok=True, message="[OK] Modelo ECG entrenado exitosamente", resultado=EntrenarModeloECG(**resultado_data)
            )
        except Exception as e:
            return EntrenarModeloECGMutation(ok=False, message=f"[ERROR] Error al entrenar modelo: {str(e)}")


# --- QUERY CONSOLIDADA ---
class Query(BaseQuery):
    obtener_clusters = graphene.List(PacienteCluster)
    obtener_historico_ecg = graphene.List(HistoricoECG, id_paciente=graphene.Int(required=True))

    def resolve_obtener_clusters(self, info):
        print("🔍 Ejecutando obtener_clusters...")
        resultado = agrupar_pacientes()
        print("Resultado:", resultado)
        if not resultado:
            print("⚠️ agrupar_pacientes devolvió vacío o None")
            return []
        return [PacienteCluster(id_triaje=r["id_triaje"], cluster=r["cluster"]) for r in resultado]

    def resolve_obtener_historico_ecg(self, info, id_paciente):
        print(f"📊 Obteniendo historial ECG para paciente {id_paciente}")
        historico_data = obtener_historico_ecg_mock(id_paciente)
        return [HistoricoECG(**h) for h in historico_data]


# --- SCHEMA GLOBAL ---
class Mutation(graphene.ObjectType):
    sincronizar_triajes = SincronizarTriajes.Field()
    obtener_triajes_riesgo = ObtenerTriajesRiesgo.Field()
    entrenar_modelo = EntrenarModelo.Field()
    entrenar_clusters = EntrenarClusters.Field()
    predecir_cluster = PredecirCluster.Field()
    # Nuevas mutations ECG
    analizar_ecg = AnalizarECGMutation.Field()
    obtener_historico_ecg = ObtenerHistoricoECGMutation.Field()
    entrenar_modelo_ecg = EntrenarModeloECGMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
