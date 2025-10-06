
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

UA = {"User-Agent": "GalileiQuiz/1.0 (contacto@tu-dominio)"}

def search_top(word: str, limit: int = 1):
    """REST: devuelve el mejor match (title, key, url) para una palabra."""
    url = "https://es.wikibooks.org/w/rest.php/v1/search/page"
    r = requests.get(url, params={"q": word, "limit": limit}, headers=UA, timeout=20)
    r.raise_for_status()
    pages = (r.json().get("pages") or [])
    if not pages:
        return None
    top = pages[0]
    key = top.get("key")
    return {"title": top.get("title"), "key": key, "url": f"https://es.wikibooks.org/wiki/{key}"}

def fetch_html_via_rest(key: str) -> str | None:
    """Trae HTML via REST. Codifica '/' como %2F para subpáginas."""
    encoded = quote(key, safe="")
    url = f"https://es.wikibooks.org/w/rest.php/v1/page/{encoded}/html"
    r = requests.get(url, headers=UA, timeout=20)
    return r.text if r.status_code == 200 else None

def fetch_html_via_action(title: str) -> str | None:
    """Fallback con Action API (parse → html)."""
    url = "https://es.wikibooks.org/w/api.php"
    params = {"action": "parse", "page": title, "prop": "text", "format": "json", "formatversion": "2"}
    r = requests.get(url, params=params, headers=UA, timeout=20)
    r.raise_for_status()
    return (r.json().get("parse") or {}).get("text")

def html_to_text(html: str) -> str:
    """Convierte HTML a texto plano básico."""
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n", strip=True)

def get_text_from_word(word: str):
    """Busca por palabra → trae HTML (REST/Action) → devuelve título, url y texto."""
    hit = search_top(word)
    if not hit:
        return None
    html = fetch_html_via_rest(hit["key"]) or fetch_html_via_action(hit["title"])
    if not html:
        return None
    text = html_to_text(html)
    return {"title": hit["title"], "key": hit["key"], "url": hit["url"], "html": html, "text": text}
