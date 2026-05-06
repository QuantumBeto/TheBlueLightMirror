from entities.sombrio import Sombrio
from entities.among_us import AmongUs
from entities.pato import Pato
from entities.freddy import Freddy
from entities.baymax import Baymax
from entities.nexo import Nexo

CHARACTER_MAP = {
    "sombrio":   Sombrio,
    "among_us":  AmongUs,
    "pato":      Pato,
    "freddy":    Freddy,
    "baymax":    Baymax,
    "nexo":      Nexo,
}

def get_character(character_id):
    """Devuelve una instancia del personaje según su ID."""
    cls = CHARACTER_MAP.get(character_id)
    if cls is None:
        raise ValueError(f"Personaje '{character_id}' no encontrado.")
    return cls()