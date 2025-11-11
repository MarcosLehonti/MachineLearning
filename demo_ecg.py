#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de demostración del sistema de reconocimiento de ECG.
Este script muestra cómo usar los nuevos endpoints GraphQL.
"""

from schema import schema


def demo_ecg_analysis():
    """Demostración de los endpoints de análisis de ECG."""

    print("=== DEMO: Sistema de Análisis de ECG ===\n")

    # 1. Análisis de ECG individual
    print("1. Analizando imagen de ECG para paciente...")
    query_analysis = """
    mutation {
        analizarEcg(archivoImagen: "ecg_paciente_123.jpg", idPaciente: 123) {
            ok
            message
            analisis {
                diagnostico
                descripcion
                nivelRiesgo
                probabilidad
                frecuenciaCardiaca
            }
        }
    }
    """

    result = schema.execute(query_analysis)
    if result.data:
        analisis = result.data["analizarEcg"]["analisis"]
        print(f"   Diagnóstico: {analisis['diagnostico']}")
        print(f"   Riesgo: {analisis['nivelRiesgo']}")
        print(f"   Probabilidad: {analisis['probabilidad']}%")
    print()

    # 2. Historial de ECG
    print("2. Obteniendo historial de ECG...")
    query_history = """
    mutation {
        obtenerHistoricoEcg(idPaciente: 123) {
            ok
            message
            historico {
                diagnostico
                nivelRiesgo
                fechaAnalisis
            }
        }
    }
    """

    result = schema.execute(query_history)
    if result.data:
        historico = result.data["obtenerHistoricoEcg"]["historico"]
        print(f"   Se encontraron {len(historico)} análisis previos:")
        for i, analisis in enumerate(historico, 1):
            print(f"     {i}. {analisis['diagnostico']} - Riesgo: {analisis['nivelRiesgo']}")
    print()

    # 3. Entrenamiento de modelo
    print("3. Entrenando modelo de ECG...")
    query_training = """
    mutation {
        entrenarModeloEcg {
            ok
            message
            resultado {
                precision
                datasetSize
                tiempoEntrenamiento
                modeloVersion
            }
        }
    }
    """

    result = schema.execute(query_training)
    if result.data:
        training = result.data["entrenarModeloEcg"]["resultado"]
        print(f"   Precisión: {training['precision']}%")
        print(f"   Dataset: {training['datasetSize']} registros")
        print(f"   Tiempo: {training['tiempoEntrenamiento']}")
    print()

    print("=== DEMO COMPLETADO ===")


if __name__ == "__main__":
    demo_ecg_analysis()
