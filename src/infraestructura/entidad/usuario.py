from dataclasses import dataclass


@dataclass(frozen=True)
class Usuario:
    alias: str
    contra: str
    