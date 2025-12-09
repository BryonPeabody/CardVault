from typing import Dict, TypedDict, List, Tuple


class ApiCodes(TypedDict):
    image: str
    price: str


SETS: Dict[str, ApiCodes] = {
    "Silver Tempest": {"image": "swsh12", "price": "Silver Tempest"},
    "Crown Zenith": {"image": "swsh12.5", "price": "Crown Zenith"},
    "Scarlet & Violet Base": {"image": "sv01", "price": "Scarlet & Violet Base"},
    "Paldea Evolved": {"image": "sv02", "price": "Paldea Evolved"},
    "Obsidian Flames": {"image": "sv03", "price": "Obsidian Flames"},
    "151": {"image": "sv03.5", "price": "151"},
    "Paradox Rift": {"image": "sv04", "price": "Paradox Rift"},
    "Paldean Fates": {"image": "sv04.5", "price": "Paldean Fates"},
    "Temporal Forces": {"image": "sv05", "price": "Temporal Forces"},
    "Twilight Masquerade": {"image": "sv06", "price": "Twilight Masquerade"},
    "Shrouded Fable": {"image": "sv06.5", "price": "Shrouded Fable"},
    "Stellar Crown": {"image": "sv07", "price": "Stellar Crown"},
    "Surging Sparks": {"image": "sv08", "price": "Surging Sparks"},
    "Prismatic Evolutions": {"image": "sv08.5", "price": "Prismatic Evolutions"},
    "Journey Together": {"image": "sv09", "price": "Journey Together"},
    "Destined Rivals": {"image": "sv10", "price": "Destined Rivals"},
    "Black Bolt": {"image": "sv10.5b", "price": "Black Bolt"},
    "White Flare": {"image": "sv10.5w", "price": "White Flare"},
}

# Derived artifacts (don’t hand-edit below)
SET_CHOICES: List[Tuple[str, str]] = [(name, name) for name in SETS.keys()]
IMAGE_SET_MAP: Dict[str, str] = {name: codes["image"] for name, codes in SETS.items()}
PRICE_SET_MAP: Dict[str, str] = {name: codes["price"] for name, codes in SETS.items()}
