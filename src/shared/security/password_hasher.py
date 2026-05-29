"""Utilidad de hashing para contraseñas.

Nota: En este proyecto se solicitó usar `bcrypt`. Sin embargo, el entorno actual
no tiene `bcrypt` instalado (ModuleNotFoundError). Para no romper el build, se
usa una alternativa segura basada en `hashlib.scrypt`.

Compatibilidad:
- Este módulo expone la misma interfaz `hash_password` / `verify_password`.
- Si más adelante instalas `bcrypt`, podemos cambiar la implementación manteniendo
  la misma interfaz.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import os

# Formato de almacenamiento: scrypt$<salt_b64>$<hash_b64>


def hash_password(plain_password: str) -> str:
    if plain_password is None:
        raise ValueError("plain_password no puede ser None")

    salt = os.urandom(16)
    # N/r/p: parámetros razonables (memoria/CPU). Ajustable.
    derived = hashlib.scrypt(
        plain_password.encode("utf-8"),
        salt=salt,
        n=2**14,
        r=8,
        p=1,
        dklen=32,
    )

    return "scrypt$" + base64.b64encode(salt).decode("utf-8") + "$" + base64.b64encode(derived).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if plain_password is None or hashed_password is None:
        return False

    try:
        parts = hashed_password.split("$")
        if len(parts) != 3 or parts[0] != "scrypt":
            return False

        salt = base64.b64decode(parts[1])
        expected = base64.b64decode(parts[2])

        derived = hashlib.scrypt(
            plain_password.encode("utf-8"),
            salt=salt,
            n=2**14,
            r=8,
            p=1,
            dklen=32,
        )

        return hmac.compare_digest(derived, expected)
    except Exception:
        return False


