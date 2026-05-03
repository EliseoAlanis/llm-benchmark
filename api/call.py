import csv
from datasets import load_dataset
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

NUM_NOTICIAS = 20
CACHE_CSV = os.path.join(os.path.dirname(__file__), "..", "resumenes_cache.csv")


def _cargar_cache() -> list[dict] | None:
    """Devuelve la lista de resúmenes si el CSV de caché existe, o None si no."""
    if not os.path.exists(CACHE_CSV):
        return None
    with open(CACHE_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        filas = list(reader)
    if len(filas) != NUM_NOTICIAS:
        return None   # caché incompleto → regenerar
    return [
        {"indice": int(r["indice"]), "resumen_humano": r["resumen_humano"], "resumen_ia": r["resumen_ia"]}
        for r in filas
    ]


def _guardar_cache(resultados: list[dict]) -> None:
    """Guarda los resúmenes en el CSV de caché."""
    with open(CACHE_CSV, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["indice", "resumen_humano", "resumen_ia"])
        writer.writeheader()
        writer.writerows(resultados)
    print(f"[call.py] ✔ Caché guardado en: {CACHE_CSV}")


def generar_resumenes(forzar: bool = False) -> tuple[list[dict], dict]:
    """
    Descarga las primeras NUM_NOTICIAS noticias del dataset MLSum en español,
    genera un resumen con IA para cada una y retorna:
        - lista de dicts: [{'indice': 0, 'resumen_humano': '...', 'resumen_ia': '...'}, ...]
        - dict de uso de tokens: {'input': int, 'output': int, 'total': int, 'llamadas': int}

    Si ya existe resumenes_cache.csv con los 20 resúmenes previos, los reutiliza
    sin hacer ninguna llamada a la API (ahorra tokens en cada re-ejecución).
    Pasá forzar=True para regenerar aunque exista el caché.
    """
    uso = {"input": 0, "output": 0, "total": 0, "llamadas": 0}

    if not forzar:
        cached = _cargar_cache()
        if cached is not None:
            print(f"[call.py] ✔ Resúmenes cargados desde caché ({CACHE_CSV}). Sin llamadas a la API.")
            return cached, uso

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    print(f"[call.py] Descargando dataset MLSum (es)...")
    ds = load_dataset("mteb/mlsum", "es", split="test")
    muestra = ds.select(range(NUM_NOTICIAS))

    prompt_sistema = (
        "Eres el editor jefe de un periódico digital. "
        "Escribe una entradilla de UNA SOLA ORACIÓN contundente (máximo 25 palabras)."
    )

    resultados = []

    for i, noticia in enumerate(muestra):
        texto_noticia = noticia["text"]
        resumen_humano = noticia["summary"]

        print(f"[call.py] Generando resumen {i + 1}/{NUM_NOTICIAS}...")

        try:
            response = client.responses.create(
                model="gpt-5.4-mini",
                input=[
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": f"Resume la siguiente noticia:\n\n{texto_noticia}"},
                ],
                max_output_tokens=100,
            )
            resumen_ia = response.output_text.strip()
            print(f"[call.py]   ✔ {resumen_ia}")

            # Acumular tokens
            if hasattr(response, "usage") and response.usage:
                uso["input"]   += response.usage.input_tokens
                uso["output"]  += response.usage.output_tokens
                uso["total"]   += response.usage.total_tokens
            uso["llamadas"] += 1

        except Exception as e:
            print(f"[call.py]   ✗ Error en noticia {i + 1}: {e}")
            resumen_ia = "ERROR"

        resultados.append({
            "indice": i,
            "resumen_humano": resumen_humano,
            "resumen_ia": resumen_ia,
        })

    print(f"[call.py] ✔ {len(resultados)} resúmenes generados.")
    _guardar_cache(resultados)
    return resultados, uso
