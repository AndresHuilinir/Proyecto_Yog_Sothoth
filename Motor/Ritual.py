# Ritual.py
import os
from Portales import cognitotrofia, resolver_plantilla
from Rezos import Plegarias, convertir_drive, descargar
from Purificacion import eterno_retorno
from Orden_universal import ruta

MODO = "visual"  # "visual" o "consola"

Plegarias()

os.makedirs(ruta("archivos"),    exist_ok=True)
os.makedirs(ruta("Confesiones"), exist_ok=True)
eterno_retorno()

df = cognitotrofia()

if MODO == "visual":
    from Interfaz import lanzar_interfaz
    lanzar_interfaz(df)

else:
    from Conocimiento import generar_imagen
    from La_puerta import las_pruebas

    fila_inicio, rango, ignorados, numero_base = las_pruebas(df, modo="consola")

    df_procesar = df.iloc[fila_inicio:].copy()
    df_procesar = df_procesar[~df_procesar.index.isin(ignorados)]
    df_procesar = df_procesar.head(rango).reset_index(drop=True)

    print(f"\nIniciando... {len(df_procesar)} confesiones. Numeración desde: {numero_base}\n")

    for i, (_, row) in enumerate(df_procesar.iterrows()):
        numero_visual          = numero_base + i
        plantilla, sede_custom = resolver_plantilla(str(row["sede"]))

        ruta_adjunto   = None
        requiere_canva = False
        link_drive     = str(row["imagen"]).strip()

        if "drive.google.com" in link_drive:
            url_directa = convertir_drive(link_drive)
            if url_directa:
                resultado = descargar(url_directa, ruta(f"archivos/adjunto_{numero_visual}"))
                if resultado == "INVALIDO":
                    requiere_canva = True
                elif resultado:
                    ruta_adjunto = resultado

        try:
            generar_imagen(
                nombre_plantilla = plantilla,
                numero           = numero_visual,
                confesion        = str(row["confesion"]),
                sede_custom      = sede_custom,
                ruta_adjunto     = ruta_adjunto,
                requiere_canva   = requiere_canva,
            )
            print(f"[OK] ID {row['id_csv']} → Imagen {numero_visual}")
        except Exception as e:
            print(f"[ERROR] ID {row['id_csv']}: {e}")

    print("\nProceso finalizado.")