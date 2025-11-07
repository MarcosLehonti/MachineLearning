from ml.model import entrenar_modelo_con_datos
from ml.clustering import entrenar_clusters

# 🔹 Entrenar modelo supervisado
print("Entrenando modelo supervisado...")
entrenar_modelo_con_datos()

# 🔹 Entrenar modelo no supervisado (K-Means)
print("Entrenando modelo de clustering...")
resultado = entrenar_clusters(num_clusters=3)
print(resultado)
