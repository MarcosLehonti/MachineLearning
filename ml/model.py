from sqlalchemy import Column, Integer, Float, String, Boolean
from db.connection import Base, SessionLocal
from ml.datos_entrenamiento import datos_hardcodeados
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import joblib
import os


# --- MODELO SQLALCHEMY ---
class TriajeML(Base):
    __tablename__ = "triajes_ml"
    
    id_triaje = Column(Integer, primary_key=True, index=True)  # No autoincrementa, será el mismo ID
    nombre_paciente = Column(String(100))
    temperatura = Column(Float)
    frecuencia_cardiaca = Column(Float)
    frecuencia_respiratoria = Column(Float)
    saturacion_oxigeno = Column(Float)
    peso = Column(Float)
    estatura = Column(Float)
    alergias = Column(String(255))
    enfermedades_cronicas = Column(String(255))
    motivo_consulta = Column(String(255))
    sufre_infarto = Column(Boolean, default=False)


# --- RUTA DEL MODELO ---
MODEL_PATH = "ml/model_infarto.pkl"


# --- ENTRENAR MODELO GENERAL ---
def entrenar_modelo(df=None):
    df = datos_hardcodeados()

    """
    Entrena el modelo con los datos dados y guarda el modelo en ml/model_infarto.pkl
    """
    X = df[["temperatura", "frecuencia_cardiaca", "frecuencia_respiratoria", "saturacion_oxigeno", "peso", "estatura"]]
    y = df["sufre_infarto"]

    # Verificación de clases
    if len(set(y)) < 2:
        raise ValueError("Los datos deben contener al menos dos clases distintas (0 y 1).")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LogisticRegression()
    model.fit(X_train, y_train)

    os.makedirs("ml", exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print("✅ Modelo entrenado y guardado en:", MODEL_PATH)


# --- ENTRENAR MODELO CON DATOS DE BD Y HARDOCODEADOS ---
def entrenar_modelo_con_datos():
    """
    Entrena el modelo combinando datos de la base de datos con datos base hardcodeados.
    """
    db = SessionLocal()
    registros = db.query(TriajeML).all()

    # Convertir datos de la BD
    data_bd = {
        "temperatura": [r.temperatura for r in registros],
        "frecuencia_cardiaca": [r.frecuencia_cardiaca for r in registros],
        "frecuencia_respiratoria": [r.frecuencia_respiratoria for r in registros],
        "saturacion_oxigeno": [r.saturacion_oxigeno for r in registros],
        "peso": [r.peso for r in registros],
        "estatura": [r.estatura for r in registros],
        "sufre_infarto": [int(r.sufre_infarto) for r in registros]
    }

    df_bd = pd.DataFrame(data_bd)
    df_hard = datos_hardcodeados()

    # Combinar ambos datasets
    if len(df_bd) > 0:
        df_final = pd.concat([df_bd, df_hard], ignore_index=True)
        print(f"✅ Entrenando modelo con {len(df_final)} registros (BD + hardcodeados).")
    else:
        print("⚠️ No hay datos en la base de datos. Entrenando solo con datos hardcodeados.")
        df_final = df_hard

    # Asegurar que existan ambas clases
    if len(set(df_final["sufre_infarto"])) < 2:
        print("⚠️ Solo existe una clase en los datos. Añadiendo ejemplos artificiales.")
        df_final = pd.concat([df_final, datos_hardcodeados()], ignore_index=True)

    try:
        entrenar_modelo(df_final)
        resultado = f"✅ Modelo entrenado con {len(df_final)} registros totales."
    except Exception as e:
        resultado = f"❌ Error al entrenar modelo: {e}"

    db.close()
    return resultado


# --- PREDICCIÓN ---
def predecir_paciente(datos):
    """
    Recibe un diccionario con los datos del paciente y predice si puede sufrir un infarto.
    """
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("❌ No se encontró el modelo entrenado. Ejecuta entrenar_modelo_con_datos() primero.")

    model = joblib.load(MODEL_PATH)

    df = pd.DataFrame([{
        "temperatura": datos["temperatura"],
        "frecuencia_cardiaca": datos["frecuencia_cardiaca"],
        "frecuencia_respiratoria": datos["frecuencia_respiratoria"],
        "saturacion_oxigeno": datos["saturacion_oxigeno"],
        "peso": datos["peso"],
        "estatura": datos["estatura"]
    }])

    prediction = model.predict(df)[0]
    prob = model.predict_proba(df)[0][1]

    return {
        "sufre_infarto": bool(prediction),
        "probabilidad": round(prob * 100, 2)
    }
