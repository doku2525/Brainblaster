import json
from typing import Any


def speicher_in_jsondatei(daten: dict, json_dateiname: str) -> None:
    # dic = daten.as_iso_dict()
    with open(json_dateiname, "w") as file:
        json.dump(daten, file, indent=4, ensure_ascii=True)


def lese_aus_jsondatei(json_dateiname: str) -> Any:
    with open(json_dateiname, "r") as file:
        data = json.load(file)
    return data
