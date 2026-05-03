import pandas as pd

# 1. Definir los precios actuales (Dólares por cada 1 Millón de tokens)
PRECIO_MINI_INPUT = 0.15
PRECIO_MINI_OUTPUT = 0.60

PRECIO_STD_INPUT = 2.50
PRECIO_STD_OUTPUT = 15.00

try:
    # 2. Cargar los resultados
    df_mini = pd.read_csv("../resultados_mlsum.csv")
    df_std = pd.read_csv("../resultados_mlsum_v2.csv")

    # 3. Sumar todos los tokens gastados en el test con el modelo MINI
    total_in_mini = df_mini['input_tokens'].sum()
    total_out_mini = df_mini['output_tokens'].sum()

    # Calcular costo en USD
    costo_mini_in = (total_in_mini / 1_000_000) * PRECIO_MINI_INPUT
    costo_mini_out = (total_out_mini / 1_000_000) * PRECIO_MINI_OUTPUT
    costo_total_mini = costo_mini_in + costo_mini_out

    # 4. Sumar todos los tokens gastados en el test con el modelo ESTÁNDAR
    total_in_std = df_std['input_tokens'].sum()
    total_out_std = df_std['output_tokens'].sum()

    # Calcular costo en USD
    costo_std_in = (total_in_std / 1_000_000) * PRECIO_STD_INPUT
    costo_std_out = (total_out_std / 1_000_000) * PRECIO_STD_OUTPUT
    costo_total_std = costo_std_in + costo_std_out

    # 5. Imprimir el reporte financiero
    print("=" * 40)
    print(" REPORTE DE COSTOS DE API - OPENAI ")
    print("=" * 40)

    print(f"\n[ GPT-5.4-MINI ]")
    print(f"Tokens totales consumidos: {total_in_mini + total_out_mini}")
    print(f"Costo exacto: ${costo_total_mini:.6f} USD")

    print(f"\n[ GPT-5.4 ESTÁNDAR ]")
    print(f"Tokens totales consumidos: {total_in_std + total_out_std}")
    print(f"Costo exacto: ${costo_total_std:.6f} USD")

    print("-" * 40)
    print(f"Diferencia de precio: El modelo estándar costó {costo_total_std / costo_total_mini:.1f} veces más.")

except FileNotFoundError as e:
    print(f"Error: Asegúrate de que los archivos CSV estén en la misma carpeta. Detalle: {e}")