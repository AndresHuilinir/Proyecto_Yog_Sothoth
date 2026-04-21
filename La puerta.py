#La puerta.py
import os
from Conocimiento import *
from Portales import *

Plegarias()
os.makedirs(ruta("archivos"), exist_ok=True)
os.makedirs(ruta("Confesiones"), exist_ok=True)
eterno_retorno()

# 1. Cargar y actualizar datos
df = cognitotrofia()

# 2. Configurar sesión
fila_inicio, rango, ignorados, numero_base = las_pruebas(df)

# 3. Filtrar
df_procesar = df[df["id_csv"] >= fila_inicio].copy()
df_procesar = df_procesar[~df_procesar["id_csv"].isin(ignorados)]
df_procesar = df_procesar.head(rango)

# 4. Generación
print(f"\nIniciando... Numeración visual empezará en: {numero_base}\n")

for i, (_, row) in enumerate(df_procesar.iterrows()):
    numero_visual = numero_base + i
    plantilla, sede_custom = resolver_plantilla(str(row["sede"]))
    
    ruta_adjunto = None
    requiere_canva = False
    link_drive = str(row["imagen"]).strip()
    
    if "drive.google.com" in link_drive:
        url_directa = convertir_drive(link_drive)
        if url_directa:
            resultado = descargar(url_directa, ruta(f"archivos/adjunto_{numero_visual}"))
            if resultado == "INVALIDO": requiere_canva = True
            elif resultado: ruta_adjunto = resultado

    try:
        generar_imagen(
            nombre_plantilla = plantilla,
            numero = numero_visual,
            confesion = str(row["confesion"]),
            sede_custom = sede_custom,
            ruta_adjunto = ruta_adjunto,
            requiere_canva = requiere_canva
        )
        print(f"[OK] ID {row['id_csv']} -> Imagen {numero_visual}")
    except Exception as e:
        print(f"[ERROR] En ID {row['id_csv']}: {e}")

print("\nProceso finalizado.")