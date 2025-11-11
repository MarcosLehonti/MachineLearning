"""
Módulo para análisis de imágenes de ECG con resultados simulados.
Implementación rápida para proyecto de prueba.
"""

import random
import time
from datetime import datetime


def analizar_ecg_mock(archivo_imagen, id_paciente):
    """
    Simula el análisis de una imagen de ECG.
    Retorna un resultado "realista" pero ficticio.

    Args:
        archivo_imagen: Nombre del archivo de imagen
        id_paciente: ID del paciente

    Returns:
        dict: Resultado del análisis simulado
    """
    print(f"[ECG] Analizando imagen: {archivo_imagen} para paciente {id_paciente}")

    # Usar hash del nombre de imagen como semilla para resultados consistentes
    seed = hash(archivo_imagen) & 0xFFFFFFFF  # Asegurar que sea positivo
    random.seed(seed)

    # Simular tiempo de procesamiento
    time.sleep(0.5)

    # Tipos de diagnóstico con probabilidades realistas
    diagnosticos = [
        {
            "tipo": "Normal",
            "probabilidad": 65,
            "descripcion": "Ritmo sinusal normal. Ondas P, QRS y T dentro de parámetros normales.",
            "riesgo": "Bajo",
        },
        {
            "tipo": "Arritmia Supraventricular",
            "probabilidad": 15,
            "descripcion": "Arritmia que se origina por encima de los ventrículos. Se requiere seguimiento.",
            "riesgo": "Medio",
        },
        {
            "tipo": "Isquemia Subendocárdica",
            "probabilidad": 10,
            "descripcion": "Cambios sugestivos de isquemia subendocárdica. Considerar evaluación adicional.",
            "riesgo": "Medio-Alto",
        },
        {
            "tipo": "Fibrilación Auricular",
            "probabilidad": 5,
            "descripcion": "Ritmo cardíaco irregular con actividad auricular caótica.",
            "riesgo": "Alto",
        },
        {
            "tipo": "Infarto Agudo",
            "probabilidad": 5,
            "descripcion": "Elevación del segmento ST sugestiva de infarto agudo. Requiere atención inmediata.",
            "riesgo": "Crítico",
        },
    ]

    # Seleccionar diagnóstico basado en probabilidades (ahora determinístico)
    rand = random.randint(1, 100)
    if rand <= 65:
        resultado = diagnosticos[0]  # Normal
    elif rand <= 80:
        resultado = diagnosticos[1]  # Arritmia
    elif rand <= 90:
        resultado = diagnosticos[2]  # Isquemia
    elif rand <= 95:
        resultado = diagnosticos[3]  # Fibrilación
    else:
        resultado = diagnosticos[4]  # Infarto

    # Añadir valores simulados de medición
    medicion_heart_rate = random.randint(60, 100)
    if resultado["tipo"] == "Fibrilación Auricular":
        medicion_heart_rate = random.randint(90, 150)
    elif resultado["tipo"] == "Infarto Agudo":
        medicion_heart_rate = random.randint(80, 130)

    return {
        "id_paciente": id_paciente,
        "archivo_imagen": archivo_imagen,
        "fecha_analisis": datetime.now().isoformat(),
        "diagnostico": resultado["tipo"],
        "descripcion": resultado["descripcion"],
        "probabilidad": resultado["probabilidad"],
        "nivel_riesgo": resultado["riesgo"],
        "frecuencia_cardiaca": medicion_heart_rate,
        "estado": "Completado",
        "tiempo_procesamiento": "0.5 segundos",
        "modelo_utilizado": "ECG-Mock-DeepLearning-v1.0",
    }


def obtener_historico_ecg_mock(id_paciente):
    """
    Simula el histórico de análisis ECG para un paciente.

    Args:
        id_paciente: ID del paciente

    Returns:
        list: Lista de análisis previos
    """
    print(f"[ECG] Obteniendo historico ECG para paciente {id_paciente}")

    # Generar 2-5 análisis previos aleatorios
    num_analisis = random.randint(2, 5)
    historico = []

    for i in range(num_analisis):
        # Fecha aleatoria en los últimos 6 meses
        dias_atras = random.randint(1, 180)
        fecha = datetime.now().replace(day=max(1, datetime.now().day - dias_atras))

        # Generar resultado aleatorio
        resultado = analizar_ecg_mock(f"ecg_hist_{i + 1}.jpg", id_paciente)
        resultado["fecha_analisis"] = fecha.isoformat()
        resultado["id_analisis"] = f"ECG_{id_paciente}_{i + 1:03d}"

        # Filtrar solo los campos que están en HistoricoECG
        historico_item = {
            "id_analisis": resultado["id_analisis"],
            "fecha_analisis": resultado["fecha_analisis"],
            "diagnostico": resultado["diagnostico"],
            "descripcion": resultado["descripcion"],
            "probabilidad": resultado["probabilidad"],
            "nivel_riesgo": resultado["nivel_riesgo"],
            "archivo_imagen": resultado["archivo_imagen"],
        }

        historico.append(historico_item)

    return historico


def entrenar_modelo_ecg_mock():
    """
    Simula el entrenamiento del modelo ECG.

    Returns:
        dict: Resultado del entrenamiento simulado
    """
    print("[ECG] Iniciando entrenamiento de modelo ECG...")
    time.sleep(1)  # Simular tiempo de entrenamiento

    return {
        "estado": "Completado",
        "precision": round(random.uniform(85.0, 95.0), 2),
        "dataset_size": random.randint(10000, 50000),
        "epocas": 50,
        "tiempo_entrenamiento": "45 minutos",
        "modelo_version": "ECG-Mock-DeepLearning-v1.0",
    }
