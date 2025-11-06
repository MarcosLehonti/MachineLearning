import requests
import os
from dotenv import load_dotenv
from db.connection import SessionLocal, init_db
from ml.model import TriajeML, predecir_paciente  # Importa el modelo actualizado

load_dotenv()

def get_triajes_from_spring():
    """Obtiene los triajes desde la API de Spring Boot (GraphQL o REST)"""
    url = os.getenv("SPRING_API")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("✅ Datos obtenidos desde el backend correctamente")
            return response.json()
        else:
            print("❌ Error al obtener triajes:", response.status_code)
            return []
    except Exception as e:
        print("⚠️ Error al conectar con el backend:", e)
        return []


def insert_triajes_into_db():
    """Inserta los triajes obtenidos en la tabla triajes_ml"""
    init_db()
    session = SessionLocal()
    data = get_triajes_from_spring()

    if not data:
        print("⚠️ No se encontraron datos para insertar.")
        return

    try:
        # Si la respuesta viene dentro de "data" → "triajes", la extraemos
        if isinstance(data, dict) and "data" in data and "triajes" in data["data"]:
            data = data["data"]["triajes"]

        for t in data:
            id_triaje = t.get("id")  # 👈 ID del backend de Spring Boot

            # Verifica si ya existe ese triaje (por id_triaje)
            exists = session.query(TriajeML).filter_by(id_triaje=id_triaje).first()
            if exists:
                continue  # Evita duplicados

            # --- Preparar datos para la predicción ---
            datos_paciente = {
                "temperatura": t.get("temperatura"),
                "frecuencia_cardiaca": t.get("frecuenciaCardiaca"),
                "frecuencia_respiratoria": t.get("frecuenciaRespiratoria"),
                "saturacion_oxigeno": t.get("saturacionOxigeno"),
                "peso": t.get("peso"),
                "estatura": t.get("estatura")
            }

            try:
                resultado_prediccion = predecir_paciente(datos_paciente)
                sufre = resultado_prediccion["sufre_infarto"]
                prob = resultado_prediccion["probabilidad"]
                print(f"🧠 Paciente '{t.get('nombrePaciente', 'Desconocido')}' → Predicción: {sufre} ({prob}%)")
            except Exception as e:
                print(f"⚠️ Error en predicción para triaje {id_triaje}:", e)
                sufre = False

            # --- Insertar en la BD local ---
            nuevo_triaje = TriajeML(
                id_triaje=id_triaje,  # 👈 ID sincronizado
                nombre_paciente=t.get("nombrePaciente"),
                temperatura=t.get("temperatura"),
                frecuencia_cardiaca=t.get("frecuenciaCardiaca"),
                frecuencia_respiratoria=t.get("frecuenciaRespiratoria"),
                saturacion_oxigeno=t.get("saturacionOxigeno"),
                peso=t.get("peso"),
                estatura=t.get("estatura"),
                alergias=t.get("alergias"),
                enfermedades_cronicas=t.get("enfermedadesCronicas"),
                motivo_consulta=t.get("motivoConsulta"),
                sufre_infarto=sufre
            )

            session.add(nuevo_triaje)

        session.commit()
        print("✅ Todos los triajes fueron insertados correctamente.")
    except Exception as e:
        print("❌ Error al insertar en la base de datos:", e)
        session.rollback()
    finally:
        session.close()
