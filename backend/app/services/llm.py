
import os, json, re, requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
APP_URL = os.getenv("APP_URL", "http://localhost:8000")
APP_TITLE = os.getenv("APP_TITLE", "Galilei Quiz Dev")
DEFAULT_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-8b-instruct:free")

def _chat(messages, model=None, temperature=0.3, max_tokens=1200):
    model = model or DEFAULT_MODEL
    if not OPENROUTER_API_KEY:
        raise RuntimeError("Configura OPENROUTER_API_KEY en .env")
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": APP_URL,
        "X-Title": APP_TITLE,
    }
    payload = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
    r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=90)
    if r.status_code != 200:
        raise RuntimeError(f"OpenRouter error {r.status_code}: {r.text}")
    return r.json()["choices"][0]["message"]["content"]

def generate_mcq(text_chunk: str, n: int = 4, model_override: str | None = None):
    txt = (text_chunk or "").strip()
    if len(txt) > 4000:
        txt = txt[:4000]
    messages = [
        {"role":"system","content":"Responde SOLO JSON válido: lista de objetos con 'question','choices'(4),'correctIndex'(0..3)."},
        {"role":"user","content": f"""Imagina que quieres capacitar a alguien sobre el contenido de este texto, genera {n} preguntas de opción múltiple (4 opciones y una correcta). Delo que consideres como cosas escenciales a saber pero no tan generales.
Devuelve únicamente JSON (sin explicaciones).
<<<
{txt}
>>>"""}
    ]
    content = _chat(messages, model=model_override or DEFAULT_MODEL)
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        m = re.search(r'(\[.*\]|\{.*\})', content, re.S)
        if not m: raise
        return json.loads(m.group(1))
