import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import joblib
import os
from db.connection import SessionLocal
from ml.model import TriajeML

MODEL_CLUSTER_PATH = "ml/model_clusters.pkl"

def entrenar_clusters(num_clusters=3):
    """
    Entrena un modelo K-Means con los datos de la BD triajes_ml.
    Agrupa pacientes según sus características fisiológicas.
    """
    db = SessionLocal()
    registros = db.query(TriajeML).all()

    if not registros:
        db.close()
        return "⚠️ No hay datos en la base de datos para agrupar."

    # Crear DataFrame con los datos clínicos
    df = pd.DataFrame([{
        "temperatura": r.temperatura,
        "frecuencia_cardiaca": r.frecuencia_cardiaca,
        "frecuencia_respiratoria": r.frecuencia_respiratoria,
        "saturacion_oxigeno": r.saturacion_oxigeno,
        "peso": r.peso,
        "estatura": r.estatura
    } for r in registros])

    # Estandarizar los datos
    scaler = StandardScaler()
    datos_scaled = scaler.fit_transform(df)

    # Entrenar modelo K-Means
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    kmeans.fit(datos_scaled)

    # Guardar modelo y scaler
    os.makedirs("ml", exist_ok=True)
    joblib.dump({"model": kmeans, "scaler": scaler}, MODEL_CLUSTER_PATH)

    db.close()
    return f"✅ Modelo K-Means entrenado con {len(df)} pacientes en {num_clusters} grupos."


def predecir_cluster(datos):
    """
    Asigna un paciente nuevo a un grupo basado en el modelo K-Means entrenado.
    """
    if not os.path.exists(MODEL_CLUSTER_PATH):
        raise FileNotFoundError("❌ No se encontró el modelo K-Means entrenado. Ejecuta entrenar_clusters().")

    modelo_guardado = joblib.load(MODEL_CLUSTER_PATH)
    kmeans = modelo_guardado["model"]
    scaler = modelo_guardado["scaler"]

    df = pd.DataFrame([{
        "temperatura": datos["temperatura"],
        "frecuencia_cardiaca": datos["frecuencia_cardiaca"],
        "frecuencia_respiratoria": datos["frecuencia_respiratoria"],
        "saturacion_oxigeno": datos["saturacion_oxigeno"],
        "peso": datos["peso"],
        "estatura": datos["estatura"]
    }])

    df_scaled = scaler.transform(df)
    cluster = kmeans.predict(df_scaled)[0]

    return {
        "cluster": int(cluster),
        "mensaje": f"El paciente pertenece al grupo {cluster}."
    }

def agrupar_pacientes():
    """
    Usa el modelo entrenado para asignar un cluster a todos los pacientes de la BD.
    Devuelve una lista con el ID del paciente y su grupo.
    """
    if not os.path.exists(MODEL_CLUSTER_PATH):
        raise FileNotFoundError("❌ No se encontró el modelo K-Means entrenado. Ejecuta entrenar_clusters().")

    # Cargar modelo y scaler
    modelo_guardado = joblib.load(MODEL_CLUSTER_PATH)
    kmeans = modelo_guardado["model"]
    scaler = modelo_guardado["scaler"]

    # Conectar a la base
    db = SessionLocal()
    registros = db.query(TriajeML).all()

    if not registros:
        db.close()
        return []

    # Crear DataFrame con los datos clínicos
    df = pd.DataFrame([{
        "id_triaje": r.id_triaje,  # 👈 reemplazado aquí
        "temperatura": r.temperatura,
        "frecuencia_cardiaca": r.frecuencia_cardiaca,
        "frecuencia_respiratoria": r.frecuencia_respiratoria,
        "saturacion_oxigeno": r.saturacion_oxigeno,
        "peso": r.peso,
        "estatura": r.estatura
    } for r in registros])

    # Escalar los datos
    datos_scaled = scaler.transform(df[[
        "temperatura", "frecuencia_cardiaca", "frecuencia_respiratoria",
        "saturacion_oxigeno", "peso", "estatura"
    ]])

    # Predecir clusters
    df["cluster"] = kmeans.predict(datos_scaled)

    db.close()

    # Convertir resultado a lista de diccionarios
    return df[["id_triaje", "cluster"]].to_dict(orient="records")  # 👈 y aquí también
