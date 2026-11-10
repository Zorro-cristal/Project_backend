from typing import Optional


def normalize_alias(alias: str) -> str:
    """Normaliza el alias eliminando espacios y convirtiéndolo a minúsculas."""
    return alias.strip().lower()

def get_client_ip(request) -> str:
    """
    Obtiene la IP del cliente confiando en encabezados de proxy si están configurados.
    En un entorno Vercel/Cloudflare, X-Forwarded-For es el estándar.
    """
    # Aquí se debería validar contra una lista de proxies confiables si fuera necesario
    # Por ahora, seguimos la recomendación de confiar en los encabezados comunes
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        # El primer elemento es la IP original
        return forwarded_for.split(",")[0].strip()
    client = getattr(request, "client", None)
    return client.host if client else "unknown"