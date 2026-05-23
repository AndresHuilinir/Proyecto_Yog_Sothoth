import pandas as pd
import os
import glob
import csv
import re
from Orden_universal import ruta, MAPA_SEDES

def resolver_plantilla(sede):
    for clave, valor in MAPA_SEDES.items():
        if clave in sede:
            return valor, None
    return "Default", sede.strip()

def cognitotrofia():
    COLUMNAS     = ["marca_temporal", "confesion", "imagen", "sede"]
    maestra_path = ruta("La llave maestra.csv")
    csv_files    = glob.glob(ruta("*.csv"))

    if not csv_files:
        raise Exception("No se encontró ningún archivo CSV.")

    def leer_csv(path):
        filas = []
        with open(path, encoding="utf-8", newline="") as f:
            reader = csv.reader(f, quotechar='"', delimiter=",", skipinitialspace=True)
            next(reader, None)  # saltar encabezado
            for row in reader:
                if not row or all(c.strip() == "" for c in row):
                    continue
                while len(row) < 4:
                    row.append("")
                filas.append({
                    "marca_temporal": row[0].strip(),
                    "confesion":      row[1].strip(),
                    "imagen":         row[2].strip(),
                    "sede":           row[3].strip(),
                })
        return pd.DataFrame(filas, columns=COLUMNAS)

    nuevos = [f for f in csv_files if f != maestra_path]

    if os.path.exists(maestra_path):
        df = leer_csv(maestra_path)
        for nuevo in nuevos:
            df_nuevo = leer_csv(nuevo)
            df = pd.concat([df, df_nuevo], ignore_index=True)
            df = df.drop_duplicates(subset=["marca_temporal", "confesion"], keep="first")
            os.remove(nuevo)
    else:
        os.rename(csv_files[0], maestra_path)
        df = leer_csv(maestra_path)
        for nuevo in nuevos[1:]:
            df_nuevo = leer_csv(nuevo)
            df = pd.concat([df, df_nuevo], ignore_index=True)
            df = df.drop_duplicates(subset=["marca_temporal", "confesion"], keep="first")
            os.remove(nuevo)

    # Guardar sin id_csv para no corromper lecturas futuras
    df.to_csv(maestra_path, index=False, header=True, encoding="utf-8")

    # Limpiar
    df = df[df["confesion"].str.strip() != ""]
    df = df[df["sede"].str.strip() != ""]
    df[["confesion", "sede", "imagen"]] = df[["confesion", "sede", "imagen"]].fillna("")
    df = df.reset_index(drop=True)
    df.insert(0, "id_csv", range(1, len(df) + 1))

    print(f"   Total de confesiones cargadas: {len(df)}")
    print(f"   Rango de IDs: {df['id_csv'].min()} → {df['id_csv'].max()}")

    return df