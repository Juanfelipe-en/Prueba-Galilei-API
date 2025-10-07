"""
Cliente para OpenRouter (Chat Completions) que genera preguntas.
- Lee API key y modelo desde variables de entorno.
- Envía instrucciones claras para devolver JSON con exactamente 'n' preguntas.
- Devuelve lista[dict] con la estructura esperada por el endpoint.
"""

import os, json, re, requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
APP_URL = os.getenv("APP_URL", "http://localhost:8000")
APP_TITLE = os.getenv("APP_TITLE", "Prueba Galilei  API")
DEFAULT_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-8b-instruct:free")

def _chat(messages, model=None, temperature=0.3, max_tokens=1200):
    """
    Llama al endpoint de OpenRouter con una lista de mensajes estilo Chat.
    """
    model = model or DEFAULT_MODEL

    # Validación mínima de seguridad si hay API key o no, lanza Runtimerror.
    if not OPENROUTER_API_KEY:
        raise RuntimeError("Configura OPENROUTER_API_KEY en .env")

    # Cabeceras requeridas/recomendadas por OpenRouter
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": APP_URL,
        "X-Title": APP_TITLE,
    }
    # Cuerpo de la petición: modelo, mensajes y parámetros de generación
    payload = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}

    # Llamada HTTP (timeout razonable para evitar colgar el servidor)
    r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=90)

    #Lanza Runtimerror si OpenRouter devuelve un status != 200.
    if r.status_code != 200:
        raise RuntimeError(f"OpenRouter error {r.status_code}: {r.text}")

    # Extraeme el contenido de la primera elección (formato estándar Chat Completions)    
    return r.json()["choices"][0]["message"]["content"]

def generate_mcq(text_chunk: str, n: int = 4, model_override: str | None = None):
    """
    Genera preguntas opción múltiple basadas en un trozo de texto.
    Parámetros:
    - text_chunk: texto base del que se extraen los conceptos para preguntar
    - n: número objetivo de preguntas a generar
    - model_override: si no es None, fuerza un modelo distinto al DEFAULT_MODEL
    """
    # Normaliza / recorta texto 
    txt = (text_chunk or "").strip()
    
    if len(txt) > 4000:
        txt = txt[:4000]
    
    
    # Prompt en estilo Chat: rol "system" para reglas, "user" con la instrucción y el texto
    messages = [
        {
            "role": "system",
            "content": (
                "Eres un generador de preguntas de opción múltiple. "
                "Devuelve SOLO JSON válido y respeta estrictamente el formato."
            ),
        },
        {
            "role": "user",
            "content": f"""
            Imagina que quieres capacitar a alguien sobre el contenido de este texto.
            Genera EXACTAMENTE {n} preguntas de opción múltiple (4 opciones y una correcta).
            Devuelve únicamente JSON, sin explicaciones ni ```.

            Formato esperado (JSON):
            [
            {{
                "question": "texto claro y breve",
                "choices": ["opción A","opción B","opción C","opción D"],
                "correctIndex": 0
            }}
            ]

            Texto fuente:
            <<<
            {txt}
            >>>
            """,
        },
    ]


    # Llamada al modelo
    content = _chat(messages, model=model_override or DEFAULT_MODEL)
    # Intento 1: parseo JSON directo (Ideal)
    try:
        return json.loads(content)
    except json.JSONDecodeError:

         # Intento 2 (fallback): extrae el primer bloque JSON (array u objeto) del texto
        m = re.search(r'(\[.*\]|\{.*\})', content, re.S)
        
        if not m: 
             # Si ni siquiera hay un bloque JSON detectable, re-lanza el error
            raise
        
        return json.loads(m.group(1))
