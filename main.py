"""
main.py — Orquestador del pipeline de evaluación de LLMs.

Flujo:
    1. call.py       → genera 20 resúmenes IA a partir de 20 noticias reales
    2. Evaluator.py  → evalúa cada resumen 25 veces (5 temps × 5 intentos) = 500 llamadas
    3. exportador.py → calcula estadísticas y exporta reporte_temperaturas.csv
"""

import sys
import os

# Asegurar que los sub-paquetes sean accesibles desde la raíz del proyecto
sys.path.insert(0, os.path.dirname(__file__))

from api.call import generar_resumenes
from evaluator.Evaluator import evaluar_resumenes
from result.exportador import exportar_reporte


def main():
    print("=" * 60)
    print("  PIPELINE DE EVALUACIÓN DE LLMs — INICIO")
    print("=" * 60)

    # ── PASO 1: Generar 20 resúmenes ─────────────────────────────
    print("\n📰 PASO 1/3 — Descargando 20 noticias y generando resúmenes con IA...")
    lista_resumenes, tokens_paso1 = generar_resumenes()
    print(f"\n  ✔ Resúmenes generados: {len(lista_resumenes)}")
    for item in lista_resumenes:
        print(f"     Noticia {item['indice'] + 1:>2}: {item['resumen_ia'][:80]}...")

    # ── PASO 2: Evaluar cada resumen con el LLM-Juez (500 llamadas) ──
    total_llamadas = len(lista_resumenes) * 25
    print(f"\n⚖️  PASO 2/3 — Evaluando los {len(lista_resumenes)} resúmenes "
          f"({total_llamadas} llamadas al juez en total)...")
    resultados, tokens_paso2 = evaluar_resumenes(lista_resumenes)
    print(f"\n  ✔ Total de evaluaciones recibidas: {len(resultados)}")

    # ── PASO 3: Calcular estadísticas y exportar CSV ──────────────
    print("\n📊 PASO 3/3 — Calculando estadísticas y exportando reporte CSV...")
    exportar_reporte(resultados, ruta_csv="reporte_temperaturas.csv")

    print("\n" + "=" * 60)
    print("  PIPELINE FINALIZADO CON ÉXITO ✔")
    print("  Archivo generado: reporte_temperaturas.csv")
    print("=" * 60)

    # ── RESUMEN DE TOKENS ─────────────────────────────────────────
    total_input  = tokens_paso1["input"]  + tokens_paso2["input"]
    total_output = tokens_paso1["output"] + tokens_paso2["output"]
    total_tokens = tokens_paso1["total"]  + tokens_paso2["total"]
    total_llam   = tokens_paso1["llamadas"] + tokens_paso2["llamadas"]

    print("\n📊 USO DE TOKENS EN EL PIPELINE:")
    print(f"  {'Paso':<30} {'Llamadas':>9} {'Input':>10} {'Output':>10} {'Total':>10}")
    print("  " + "-" * 65)
    print(f"  {'Paso 1 — Generación resúmenes':<30} {tokens_paso1['llamadas']:>9} "
          f"{tokens_paso1['input']:>10} {tokens_paso1['output']:>10} {tokens_paso1['total']:>10}")
    print(f"  {'Paso 2 — Evaluación (juez)':<30} {tokens_paso2['llamadas']:>9} "
          f"{tokens_paso2['input']:>10} {tokens_paso2['output']:>10} {tokens_paso2['total']:>10}")
    print("  " + "-" * 65)
    print(f"  {'TOTAL':<30} {total_llam:>9} {total_input:>10} {total_output:>10} {total_tokens:>10}")
    print()


if __name__ == "__main__":
    main()
