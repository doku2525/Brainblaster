import json
from typing import Any
import zipfile
import datetime
from threading import Thread


def speicher_in_jsondatei(daten: dict, json_dateiname: str) -> None:
    # dic = daten.as_iso_dict()
    with open(json_dateiname, "w") as file:
        json.dump(daten, file, indent=4, ensure_ascii=True)


def lese_aus_jsondatei(json_dateiname: str) -> Any:
    with open(json_dateiname, "r") as file:
        data = json.load(file)
    return data


def schreibe_backup(dateien: list, pfad: str) -> Thread:
    """
    Erstellt ein ZIP-Archiv mit allen Dateien aus der übergebenen Liste.

    Args:
        dateien (list): Eine Liste von Dateipfaden.
        pfad (str): Der Basispfad für das Backup-Archiv.
    """
    def speicher_als_zip(dateiliste: list, backup_pfad: str) -> None:
        zeitstempel = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        backup_datei = f"{backup_pfad}/{zeitstempel}.bzip"

        with zipfile.ZipFile(backup_datei, "w", compression=zipfile.ZIP_BZIP2, compresslevel=9) as zipf:
            for datei in dateiliste:
                zipf.write(datei)

    speicher_thread = Thread(target=speicher_als_zip, args=(dateien, pfad))
    speicher_thread.start()
    return speicher_thread
