import csv
import statistics
from collections import defaultdict


def exportar_reporte(resultados: list, ruta_csv: str = "reporte_temperaturas.csv") -> None:
    """
    Recibe la lista de resultados de Evaluator.py (20 noticias × 25 llamadas = 500 items).
    Agrupa por noticia_id + temperatura, calcula estadísticas y exporta el CSV.

    Columnas del CSV:
        Noticia_ID, Temperatura, Nota_1..Nota_5, Promedio, Desvio_Estandar
    """

    # 1. Agrupar notas por (noticia_id, temperatura)
    grupos: dict[tuple, list] = defaultdict(list)
    for r in resultados:
        clave = (r["noticia_id"], r["temperatura"])
        grupos[clave].append(r["nota"])

    # 2. Construir filas ordenadas por noticia_id y luego por temperatura
    filas = []
    for clave in sorted(grupos.keys()):
        noticia_id, temperatura = clave
        notas = grupos[clave]

        notas_validas = [n for n in notas if n is not None]

        if len(notas_validas) >= 2:
            promedio = round(statistics.mean(notas_validas), 4)
            desvio = round(statistics.stdev(notas_validas), 4)
        elif len(notas_validas) == 1:
            promedio = round(float(notas_validas[0]), 4)
            desvio = 0.0
        else:
            promedio = None
            desvio = None

        notas_csv = notas + [None] * (5 - len(notas))

        filas.append({
            "Noticia_ID": noticia_id + 1,
            "Temperatura": temperatura,
            "Nota_1": notas_csv[0],
            "Nota_2": notas_csv[1],
            "Nota_3": notas_csv[2],
            "Nota_4": notas_csv[3],
            "Nota_5": notas_csv[4],
            "Promedio": promedio,
            "Desvio_Estandar": desvio,
            "_desvio_interno": desvio,   # campo auxiliar, no se escribe al CSV
        })

    # 3. Escribir el CSV
    columnas = [
        "Noticia_ID", "Temperatura",
        "Nota_1", "Nota_2", "Nota_3", "Nota_4", "Nota_5",
        "Promedio", "Desvio_Estandar",
    ]

    with open(ruta_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columnas, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(filas)

    print(f"[exportador.py] ✔ Reporte guardado en: {ruta_csv} ({len(filas)} filas)")

    # 4. Resumen en consola (una línea por temperatura)
    #    - Promedio_Global : media de los promedios de las noticias      → nivel de calidad promedio
    #    - Desvio_Promedio : media de los desvíos internos por noticia   → qué tan consistente es el modelo
    #      (hipótesis: a mayor temperatura, mayor Desvio_Promedio)
    resumen_por_temp_proms:   dict[float, list] = defaultdict(list)
    resumen_por_temp_desvios: dict[float, list] = defaultdict(list)

    for fila in filas:
        temp = fila["Temperatura"]
        if fila["Promedio"] is not None:
            resumen_por_temp_proms[temp].append(fila["Promedio"])
        if fila["_desvio_interno"] is not None:
            resumen_por_temp_desvios[temp].append(fila["_desvio_interno"])

    print("\n[exportador.py] Resumen por temperatura:")
    print(f"  {'Temperatura':<14} {'Promedio_Global':<18} {'Desvio_Promedio':<18} {'N_noticias'}")
    print("  " + "-" * 60)
    for temp in sorted(resumen_por_temp_proms.keys()):
        proms   = resumen_por_temp_proms[temp]
        desvios = resumen_por_temp_desvios[temp]

        prom_global    = round(statistics.mean(proms),   4) if proms   else None
        desvio_promedio = round(statistics.mean(desvios), 4) if desvios else None

        print(f"  {temp:<14} {str(prom_global):<18} {str(desvio_promedio):<18} {len(proms)}")
