import pandas as pd
import os
import glob
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
        return pd.read_csv(
            path,
            encoding="utf-8",
            engine="python",
            names=COLUMNAS,
            header=0,
            on_bad_lines="warn",
            dtype=str,
        )

    nuevos = [f for f in csv_files if f != maestra_path]

    if os.path.exists(maestra_path):
        df = leer_csv(maestra_path)
        for nuevo in nuevos:
            df = pd.concat([df, leer_csv(nuevo)], ignore_index=True)
            df = df.drop_duplicates(subset=["marca_temporal", "confesion"], keep="first")
            os.remove(nuevo)
    else:
        os.rename(csv_files[0], maestra_path)
        df = leer_csv(maestra_path)
        for nuevo in nuevos[1:]:
            df = pd.concat([df, leer_csv(nuevo)], ignore_index=True)
            df = df.drop_duplicates(subset=["marca_temporal", "confesion"], keep="first")
            os.remove(nuevo)

    df.to_csv(maestra_path, index=False, header=True, encoding="utf-8")
    df = df.dropna(subset=["confesion", "sede"], how="all")
    df[["confesion", "sede", "imagen"]] = df[["confesion", "sede", "imagen"]].fillna("")
    df = df.reset_index(drop=True)
    df.insert(0, "id_csv", range(1, len(df) + 1))

    return df