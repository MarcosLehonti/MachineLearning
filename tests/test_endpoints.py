"""
Tests unitarios para el sistema de reconocimiento de ECG.
Ejecuta: python tests/test_endpoints.py
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from schema import schema


def test_analisis_ecg_normal():
    """Test 1: Análisis de ECG con resultado Normal"""
    print("🧪 Test 1: Análisis ECG Normal")

    query = """
    mutation {
        analizarEcg(archivoImagen: "ecg_normal_test.jpg", idPaciente: 1) {
            ok
            message
            analisis {
                diagnostico
                nivelRiesgo
                probabilidad
            }
        }
    }
    """

    result = schema.execute(query)

    if result.errors:
        print(f"❌ ERROR: {result.errors}")
        return False

    if result.data and result.data["analizarEcg"]["ok"]:
        analisis = result.data["analizarEcg"]["analisis"]
        print(f"✅ Diagnóstico: {analisis['diagnostico']}")
        print(f"✅ Riesgo: {analisis['nivelRiesgo']}")
        print(f"✅ Probabilidad: {analisis['probabilidad']}%")
        return True
    else:
        print("❌ El test falló: no se obtuvo análisis válido")
        return False


def test_analisis_ecg_critico():
    """Test 2: Análisis de ECG con resultado crítico"""
    print("\n🧪 Test 2: Análisis ECG Crítico")

    query = """
    mutation {
        analizarEcg(archivoImagen: "ecg_critico.jpg", idPaciente: 2) {
            ok
            message
            analisis {
                diagnostico
                descripcion
                nivelRiesgo
                frecuenciaCardiaca
            }
        }
    }
    """

    result = schema.execute(query)

    if result.errors:
        print(f"❌ ERROR: {result.errors}")
        return False

    if result.data and result.data["analizarEcg"]["ok"]:
        analisis = result.data["analizarEcg"]["analisis"]
        print(f"✅ Diagnóstico: {analisis['diagnostico']}")
        print(f"✅ Riesgo: {analisis['nivelRiesgo']}")
        print(f"✅ FC: {analisis['frecuenciaCardiaca']} bpm")
        return True
    else:
        print("❌ El test falló: no se obtuvo análisis válido")
        return False


def test_historico_ecg():
    """Test 3: Obtener historial de ECG"""
    print("\n🧪 Test 3: Historial ECG")

    query = """
    mutation {
        obtenerHistoricoEcg(idPaciente: 3) {
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

    result = schema.execute(query)

    if result.errors:
        print(f"❌ ERROR: {result.errors}")
        return False

    if result.data and result.data["obtenerHistoricoEcg"]["ok"]:
        historico = result.data["obtenerHistoricoEcg"]["historico"]
        print(f"✅ Registros encontrados: {len(historico)}")
        for i, analisis in enumerate(historico[:3], 1):
            print(f"  {i}. {analisis['diagnostico']} - {analisis['nivelRiesgo']}")
        return True
    else:
        print("❌ El test falló: no se obtuvo historial válido")
        return False


def test_entrenamiento():
    """Test 4: Entrenamiento de modelo"""
    print("\n🧪 Test 4: Entrenamiento de Modelo")

    query = """
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

    result = schema.execute(query)

    if result.errors:
        print(f"❌ ERROR: {result.errors}")
        return False

    if result.data and result.data["entrenarModeloEcg"]["ok"]:
        training = result.data["entrenarModeloEcg"]["resultado"]
        print(f"✅ Precisión: {training['precision']}%")
        print(f"✅ Dataset: {training['datasetSize']:,} registros")
        print(f"✅ Tiempo: {training['tiempoEntrenamiento']}")
        return True
    else:
        print("❌ El test falló: entrenamiento no exitoso")
        return False


def test_existing_endpoints():
    """Test 5: Verificar que endpoints existentes siguen funcionando"""
    print("\n🧪 Test 5: Endpoints Existentes")

    # Test query hello
    result = schema.execute("{ hello }")
    if result.data and "hello" in result.data:
        print("✅ Endpoint 'hello' funcionando")
    else:
        print("❌ Endpoint 'hello' falló")
        return False

    # Test obtener clusters (si hay datos)
    result = schema.execute("{ obtenerClusters { idTriaje cluster } }")
    if result.data:
        print("✅ Endpoint 'obtenerClusters' funcionando")
        clusters = result.data.get("obtenerClusters", [])
        print(f"  Registros: {len(clusters)}")
    else:
        print("⚠️ Endpoint 'obtenerClusters' sin datos (normal si DB vacía)")

    return True


def run_all_tests():
    """Ejecutar todos los tests"""
    print("=" * 50)
    print("INICIANDO SUITE DE TESTS - SISTEMA ECG")
    print("=" * 50)

    tests = [
        ("Análisis ECG Normal", test_analisis_ecg_normal),
        ("Análisis ECG Crítico", test_analisis_ecg_critico),
        ("Historial ECG", test_historico_ecg),
        ("Entrenamiento Modelo", test_entrenamiento),
        ("Endpoints Existentes", test_existing_endpoints),
    ]

    passed = 0
    total = len(tests)

    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {name}: PASSED")
            else:
                print(f"❌ {name}: FAILED")
        except Exception as e:
            print(f"💥 {name}: EXCEPTION - {str(e)}")

    print("\n" + "=" * 50)
    print(f"RESULTADOS: {passed}/{total} tests exitosos")
    print(f"Tasa de éxito: {(passed / total) * 100:.1f}%")
    print("=" * 50)

    if passed == total:
        print("🎉 TODOS LOS TESTS PASARON - SISTEMA COMPLETAMENTE FUNCIONAL")
    else:
        print("⚠️ Algunos tests fallaron - Revisar implementación")


if __name__ == "__main__":
    run_all_tests()
