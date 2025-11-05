from typing import Dict, TypedDict, List, Tuple


class ApiCodes(TypedDict):
    image: str
    price: str


SETS: Dict[str, ApiCodes] = {
    "Silver Tempest": {"image": "swsh12", "price": "swsh12"},
    "Crown Zenith": {"image": "swsh12.5", "price": "swsh12pt5"},
    "Scarlet & Violet Base": {"image": "sv01", "price": "sv1"},
    "Paldea Evolved": {"image": "sv02", "price": "sv2"},
    "Obsidian Flames": {"image": "sv03", "price": "sv3"},
    "151": {"image": "sv03.5", "price": "sv3pt5"},
    "Paradox Rift": {"image": "sv04", "price": "sv4"},
    "Paldean Fates": {"image": "sv04.5", "price": "sv4pt5"},
    "Temporal Forces": {"image": "sv05", "price": "sv5"},
    "Twilight Masquerade": {"image": "sv06", "price": "sv6"},
    "Shrouded Fable": {"image": "sv06.5", "price": "sv6pt5"},
    "Stellar Crown": {"image": "sv07", "price": "sv7"},
    "Surging Sparks": {"image": "sv08", "price": "sv8"},
    "Prismatic Evolutions": {"image": "sv08.5", "price": "sv8pt5"},
    "Journey Together": {"image": "sv09", "price": "sv9"},
    "Destined Rivals": {"image": "sv10", "price": "sv10"},
    "Black Bolt": {"image": "sv10.5b", "price": "zsv10pt5"},
    "White Flare": {"image": "sv10.5w", "price": "rsv10pt5"},
}

# Derived artifacts (don’t hand-edit below)
SET_CHOICES: List[Tuple[str, str]] = [(name, name) for name in SETS.keys()]
IMAGE_SET_MAP: Dict[str, str] = {name: codes["image"] for name, codes in SETS.items()}
PRICE_SET_MAP: Dict[str, str] = {name: codes["price"] for name, codes in SETS.items()}
