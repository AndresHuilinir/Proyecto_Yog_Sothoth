import Conocimiento

# =========================
# AJUSTA ESTE VALOR
# Mueve el rectángulo censurador hacia arriba (negativo) o abajo (positivo)
# Ejemplo: -3 sube 3px, 0 sin desfase, 5 baja 5px
# =========================
desfase_del_censurador = 15

# =========================
# PARAMETROS DE PRUEBA
# =========================
PLANTILLA  = "Viña"       # CC, Conce, SJ, Viña, Vita, Default
NUMERO     = 9999
SEDE_CUSTOM = None      # solo si PLANTILLA es "Default"
TEXTO = (
    "Esta es una confesión de prueba con palabras como "
    "ctm y pico para ver cómo funciona el censurador. "
    "También tiene groserias como pixula y conchetumare "
    "para verificar que el desfase quede bien ajustado. "
    "El resto del texto queda intacto y legible."
    "maraca reconchetumare"
)

# =========================
# EJECUCIÓN
# =========================
if __name__ == '__main__':
    Conocimiento.DESFASE_CENSURADOR = desfase_del_censurador

    from Orden_universal import CARPETA_CONFESIONES
    import os
    os.makedirs(CARPETA_CONFESIONES, exist_ok=True)

    Conocimiento.generar_imagen(
        nombre_plantilla = PLANTILLA,
        numero           = NUMERO,
        confesion        = TEXTO,
        sede_custom      = SEDE_CUSTOM,
    )

    print(f"[OK] Imagen de prueba guardada en Confesiones/Confesion {NUMERO}.png")
    print(f"     Desfase usado: {desfase_del_censurador}")