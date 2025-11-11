# Ejemplos de Respuestas JSON del Sistema ECG

## ✅ Análisis de ECG Exitoso

### Respuesta Normal

```json
{
    "data": {
        "analizarEcg": {
            "ok": true,
            "message": "[OK] Análisis ECG completado para paciente 123",
            "analisis": {
                "diagnostico": "Normal",
                "descripcion": "Ritmo sinusal normal. Ondas P, QRS y T dentro de parámetros normales.",
                "nivelRiesgo": "Bajo",
                "probabilidad": 65,
                "frecuenciaCardiaca": 78,
                "archivoImagen": "ecg_paciente_123.jpg",
                "fechaAnalisis": "2024-11-11T00:10:00",
                "idAnalisis": "ECG_123_001"
            }
        }
    }
}
```

### Respuesta Crítica

```json
{
    "data": {
        "analizarEcg": {
            "ok": true,
            "message": "[OK] Análisis ECG completado para paciente 789",
            "analisis": {
                "diagnostico": "Infarto Agudo",
                "descripcion": "Elevación del segmento ST sugestiva de infarto agudo. Requiere atención inmediata.",
                "nivelRiesgo": "Crítico",
                "probabilidad": 89,
                "frecuenciaCardiaca": 115,
                "archivoImagen": "ecg_urgente_789.jpg",
                "fechaAnalisis": "2024-11-11T00:10:00",
                "idAnalisis": "ECG_789_001"
            }
        }
    }
}
```

## 📊 Historial de ECG

### Respuesta Completa

```json
{
    "data": {
        "obtenerHistoricoEcg": {
            "ok": true,
            "message": "[OK] Historial ECG obtenido para paciente 456",
            "historico": [
                {
                    "idAnalisis": "ECG_456_001",
                    "fechaAnalisis": "2024-10-15T10:30:00",
                    "diagnostico": "Normal",
                    "descripcion": "Ritmo sinusal normal.",
                    "nivelRiesgo": "Bajo",
                    "probabilidad": 72,
                    "archivoImagen": "ecg_456_001.jpg"
                },
                {
                    "idAnalisis": "ECG_456_002",
                    "fechaAnalisis": "2024-10-10T14:15:00",
                    "diagnostico": "Arritmia Supraventricular",
                    "descripcion": "Arritmia que se origina por encima de los ventrículos.",
                    "nivelRiesgo": "Medio",
                    "probabilidad": 15,
                    "archivoImagen": "ecg_456_002.jpg"
                },
                {
                    "idAnalisis": "ECG_456_003",
                    "fechaAnalisis": "2024-09-28T09:45:00",
                    "diagnostico": "Isquemia Subendocárdica",
                    "descripcion": "Cambios sugestivos de isquemia subendocárdica.",
                    "nivelRiesgo": "Medio-Alto",
                    "probabilidad": 10,
                    "archivoImagen": "ecg_456_003.jpg"
                }
            ]
        }
    }
}
```

## 🤖 Entrenamiento de Modelo

### Respuesta Exitosa

```json
{
    "data": {
        "entrenarModeloEcg": {
            "ok": true,
            "message": "[OK] Modelo ECG entrenado exitosamente",
            "resultado": {
                "estado": "Completado",
                "precision": 92.34,
                "datasetSize": 23729,
                "epocas": 50,
                "tiempoEntrenamiento": "45 minutos",
                "modeloVersion": "ECG-Mock-DeepLearning-v1.0",
                "fechaEntrenamiento": "2024-11-11T00:10:00"
            }
        }
    }
}
```

## ❌ Respuestas de Error

### Error: Parámetros Faltantes

```json
{
    "errors": [
        {
            "message": "Field 'analizarEcg' argument 'archivoImagen' of type 'String!' is required, but it was not provided.",
            "locations": [
                {
                    "line": 2,
                    "column": 3
                }
            ]
        }
    ]
}
```

### Error: Paciente No Válido

```json
{
    "data": {
        "analizarEcg": {
            "ok": false,
            "message": "[ERROR] Error al analizar ECG: Paciente no válido",
            "analisis": null
        }
    }
}
```

### Error: Sistema No Disponible

```json
{
    "data": {
        "entrenarModeloEcg": {
            "ok": false,
            "message": "[ERROR] Error al entrenar modelo: Servicio temporalmente no disponible",
            "resultado": null
        }
    }
}
```

## 🏥 Datos para Frontend

### Formato para Tabla de Resultados

```json
{
    "paciente_id": 123,
    "nombre_paciente": "Juan Pérez",
    "archivo_ecg": "ecg_paciente_123.jpg",
    "analisis_actual": {
        "diagnostico": "Normal",
        "nivel_riesgo": "Bajo",
        "probabilidad": 65,
        "frecuencia_cardiaca": 78,
        "fecha_analisis": "2024-11-11T00:10:00"
    },
    "historico_count": 3,
    "ultimo_cambio": "2024-10-15T10:30:00",
    "alerta": false
}
```

### Formato para Alertas

```json
{
    "alerta_critica": true,
    "paciente_id": 789,
    "tipo_alerta": "INFARTO_AGUDO",
    "mensaje": "Posible infarto agudo detectado",
    "descripcion": "Elevación del segmento ST sugestiva de infarto agudo. Requiere atención inmediata.",
    "nivel_riesgo": "Crítico",
    "probabilidad": 89,
    "accion_recomendada": "Revisión médica inmediata",
    "timestamp": "2024-11-11T00:10:00",
    "urgencia": "MÁXIMA"
}
```

## 📈 Métricas del Sistema

### Estadísticas Generales

```json
{
    "total_analisis": 1247,
    "pacientes_unicos": 156,
    "diagnosticos_por_categoria": {
        "Normal": 811,
        "Arritmia Supraventricular": 187,
        "Isquemia Subendocárdica": 125,
        "Fibrilación Auricular": 62,
        "Infarto Agudo": 62
    },
    "precision_modelo": 92.34,
    "ultima_actualizacion": "2024-11-11T00:10:00"
}
```

### Alertas por Período

```json
{
    "periodo": "24h",
    "total_alertas": 12,
    "alertas_criticas": 3,
    "alertas_altas": 5,
    "alertas_medias": 4,
    "pacientes_afectados": 12
}
```

## 🔄 Ejemplo de Flujo Completo

### Paso 1: Análisis Inicial

```json
{
    "data": {
        "analizarEcg": {
            "ok": true,
            "message": "Análisis completado",
            "analisis": {
                "diagnostico": "Normal",
                "nivelRiesgo": "Bajo",
                "probabilidad": 68
            }
        }
    }
}
```

### Paso 2: Seguimiento (días después)

```json
{
    "data": {
        "analizarEcg": {
            "ok": true,
            "message": "Análisis completado",
            "analisis": {
                "diagnostico": "Arritmia Supraventricular",
                "nivelRiesgo": "Medio",
                "probabilidad": 22
            }
        }
    }
}
```

### Paso 3: Consulta de Historial

```json
{
    "data": {
        "obtenerHistoricoEcg": {
            "ok": true,
            "message": "Historial obtenido",
            "historico": [
                {
                    "diagnostico": "Normal",
                    "nivelRiesgo": "Bajo",
                    "fechaAnalisis": "2024-11-08T10:00:00"
                },
                {
                    "diagnostico": "Arritmia Supraventricular",
                    "nivelRiesgo": "Medio",
                    "fechaAnalisis": "2024-11-11T00:10:00"
                }
            ]
        }
    }
}
```

## ⚡ Respuestas Rápidas

### Health Check

```json
{
    "data": {
        "hello": "Microservicio ML operativo y conectado a la base de datos"
    }
}
```

### Error de Conexión

```json
{
    "errors": [
        {
            "message": "Connection error",
            "locations": [{ "line": 1, "column": 1 }]
        }
    ]
}
```
