from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

TEMPERATURAS = [0.0, 0.5, 1.0, 1.5, 2.0]
INTENTOS_POR_TEMPERATURA = 1

PROMPT_JUEZ = (
    "Eres un evaluador. Califica el resumen de la IA del 1 al 10 basándote en qué tan bien "
    "capturó la idea del original. Responde ÚNICAMENTE con un número entero del 1 al 10."
)


def evaluar_resumenes(lista_resumenes: list[dict]) -> tuple[list[dict], dict]:
    """
    Recibe una lista de dicts con 'indice', 'resumen_humano' y 'resumen_ia'.
    Por cada noticia ejecuta 25 llamadas al LLM-Juez (5 temps × 5 intentos).
    Total de llamadas = len(lista_resumenes) × 25.

    Retorna:
        - lista de dicts: [{'noticia_id': 0, 'temperatura': 0.0, 'intento': 1, 'nota': 7}, ...]
        - dict de uso de tokens: {'input': int, 'output': int, 'total': int, 'llamadas': int}
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    resultados = []
    uso = {"input": 0, "output": 0, "total": 0, "llamadas": 0}
    total_noticias = len(lista_resumenes)
    llamada_global = 0
    total_llamadas = total_noticias * len(TEMPERATURAS) * INTENTOS_POR_TEMPERATURA

    for item in lista_resumenes:
        noticia_id = item["indice"]
        resumen_humano = item["resumen_humano"]
        resumen_ia = item["resumen_ia"]

        print(f"\n[Evaluator.py] ══ Noticia {noticia_id + 1}/{total_noticias} ══")

        mensaje_usuario = (
            f"Resumen Original (humano): {resumen_humano}\n\n"
            f"Resumen de la IA: {resumen_ia}"
        )

        for temperatura in TEMPERATURAS:
            print(f"[Evaluator.py]   Temperatura {temperatura}")

            for intento in range(1, INTENTOS_POR_TEMPERATURA + 1):
                llamada_global += 1
                print(
                    f"[Evaluator.py]     Llamada {llamada_global}/{total_llamadas} "
                    f"(noticia={noticia_id + 1}, temp={temperatura}, intento={intento})..."
                )

                try:
                    response = client.responses.create(
                        model="gpt-5.4-mini",
                        input=[
                            {"role": "system", "content": PROMPT_JUEZ},
                            {"role": "user", "content": mensaje_usuario},
                        ],
                        max_output_tokens=50,
                        temperature=temperatura,
                    )

                    texto_respuesta = response.output_text.strip()

                    try:
                        nota = int(texto_respuesta)
                    except ValueError:
                        digitos = [c for c in texto_respuesta if c.isdigit()]
                        nota = int(digitos[0]) if digitos else None

                    print(f"[Evaluator.py]     → Nota: {nota}/10")

                    # Acumular tokens
                    if hasattr(response, "usage") and response.usage:
                        uso["input"]  += response.usage.input_tokens
                        uso["output"] += response.usage.output_tokens
                        uso["total"]  += response.usage.total_tokens
                    uso["llamadas"] += 1

                except Exception as e:
                    print(f"[Evaluator.py]     ✗ Error: {e}")
                    nota = None

                resultados.append({
                    "noticia_id": noticia_id,
                    "temperatura": temperatura,
                    "intento": intento,
                    "nota": nota,
                })

    print(f"\n[Evaluator.py] ✔ Evaluación completada: {len(resultados)} resultados.")
    return resultados, uso
