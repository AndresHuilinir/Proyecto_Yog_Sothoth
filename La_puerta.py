from Portales import cognitotrofia
from Orden_universal import OFFSET_ID

def indecision(df, id_target, accion_texto):
    fila = df[df["id_csv"] == id_target - OFFSET_ID]
    if not fila.empty:
        texto    = str(fila.iloc[0]["confesion"]).strip()
        resumen  = (texto[:70] + "...") if len(texto) > 70 else texto
        confirma = input(
            f'\n¿Quieres {accion_texto} la confesión "{resumen}" (ID {id_target})? (S/N): '
        ).strip().upper()
        return confirma == "S"
    else:
        print(f"-> Error: No se encontró el ID {id_target}.")
        return False

def las_pruebas(df):
    print("\n--- [LAS PRUEBAS: Configuración de Sesión] ---")
    print(f"   Total de filas disponibles: {len(df)}")
    print(f"   Rango de IDs: {df['id_csv'].min() + OFFSET_ID} → {df['id_csv'].max() + OFFSET_ID}\n")

    # 1. Fila de inicio
    while True:
        try:
            fila_inicio = int(input("¿Desde qué ID deseas comenzar?: "))
            if indecision(df, fila_inicio, "comenzar desde"):
                break
        except ValueError:
            print("Ingresa un número válido.")

    # 2. Rango
    while True:
        try:
            rango = int(input("\n¿Cuántas confesiones procesar?: "))
            if rango >= 1:
                break
            print("Debe ser 1 o mayor.")
        except ValueError:
            print("Ingresa un número válido.")

    # 3. IDs a ignorar
    ignorados = set()
    print("\n--- Modo Ignorar ---")
    while True:
        entrada = input("ID a ignorar (X para terminar): ").strip().upper()
        if entrada == "X":
            break
        try:
            id_ignorar = int(entrada)
            if indecision(df, id_ignorar, "ignorar"):
                ignorados.add(id_ignorar - OFFSET_ID)
                print(f"-> ID {id_ignorar} agregado a ignorados.\n")
            else:
                print("-> Cancelado.\n")
        except ValueError:
            print("Ingresa un número válido o X para terminar.")

    # 4. Número base visual
    while True:
        try:
            numero_base = int(input("\n¿Con qué número visual quieres empezar?: "))
            break
        except ValueError:
            numero_base = 1
            break

    return fila_inicio - OFFSET_ID, rango, ignorados, numero_base