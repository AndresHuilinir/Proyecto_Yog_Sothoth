from Orden_universal import ruta

desfase = 4

def indecision(df, id_target, accion_texto):
    idx = id_target - desfase
    if 0 <= idx < len(df):
        texto    = str(df.iloc[idx]["confesion"]).strip()
        resumen  = (texto[:70] + "...") if len(texto) > 70 else texto
        confirma = input(
            f'\n¿Quieres {accion_texto} la confesión "{resumen}" (ID {id_target})? (S/N): '
        ).strip().upper()
        return confirma == "S"
    else:
        print(f"-> Error: ID {id_target} fuera de rango (1 → {len(df)}).")
        return False

def las_pruebas(df, modo="consola"):
    print("\n--- [LAS PRUEBAS: Configuración de Sesión] ---")
    print(f"   Total de confesiones: {len(df)}")
    print(f"   Rango de IDs: 1 → {len(df)}\n")

    # 1. Fila de inicio (siempre se pregunta)
    while True:
        try:
            fila_inicio = int(input("¿Desde qué ID deseas comenzar?: "))
            if indecision(df, fila_inicio, "comenzar desde"):
                break
        except ValueError:
            print("Ingresa un número válido.")

    # 2. Rango (solo en consola)
    if modo == "consola":
        while True:
            try:
                rango = int(input("\n¿Cuántas confesiones procesar?: "))
                if rango >= 1:
                    break
                print("Debe ser 1 o mayor.")
            except ValueError:
                print("Ingresa un número válido.")
    else:
        rango = len(df)  # en visual procesa todo

    # 3. IDs a ignorar (solo en consola)
    ignorados = set()
    if modo == "consola":
        print("\n--- Modo Ignorar ---")
        while True:
            entrada = input("ID a ignorar (X para terminar): ").strip().upper()
            if entrada == "X":
                break
            try:
                id_ignorar = int(entrada)
                if indecision(df, id_ignorar, "ignorar"):
                    ignorados.add(id_ignorar - desfase)
                    print(f"-> ID {id_ignorar} agregado a ignorados.\n")
                else:
                    print("-> Cancelado.\n")
            except ValueError:
                print("Ingresa un número válido o X para terminar.")

    # 4. Número base visual (siempre se pregunta)
    while True:
        try:
            numero_base = int(input("\n¿Con qué número visual quieres empezar?: "))
            break
        except ValueError:
            numero_base = 1
            break

    fila_inicio_idx = fila_inicio - desfase
    return fila_inicio_idx, rango, ignorados, numero_base