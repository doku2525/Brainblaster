import sys
import pickle
import json
import src.classes.vokabelkarte as vk
import src.classes.vokabelbox as vb
import src.classes.lerneinheit as le
from src.repositories.vokabelkarten_repository import InMemoryVokabelkartenRepository, JSONDateiformatVokabelkarte
from src.repositories.vokabelbox_repository import InMemeoryVokabelboxRepository, JSONDateiformatVokabelbox

sys.path.append("/home/doku/Downloads/Vokabeltrainer_SERVERVERSION")
# Damit pickle die Struktur erkennt die alten Klassen importiert
from vokabelkarte import Vokabelkarte
from vokabelbox import Vokabelbox
import lerneinheit as le_alt

def lade_pickle_datei(dateipfad):
    """Lädt eine Binärdatei mit pickle."""
    with open(dateipfad, "rb") as datei:
        return pickle.load(datei)


def speichere_json(dateipfad, daten):
    """Speichert die gegebenen Daten in einer JSON-Datei."""
    with open(dateipfad, "w", encoding="utf-8") as datei:
        json.dump(daten, datei, ensure_ascii=False, indent=4)


def convert_lerneinheit_chinesisch(alt: le_alt.LerneinheitChinesisch) -> le.LerneinheitChinesisch:
    return le.LerneinheitChinesisch(
        eintrag=alt.eintrag,
        beschreibung=alt.beschreibung,
        erzeugt=alt.erzeugt,
        traditionell=alt.traditionell,
        daten=alt.daten,
        pinyin=alt.pinyin,
        zhuyin=alt.zhuyin
    ) if not alt.eintrag.startswith("ChinEint") else None


def konvertiere_vokabelkarten(alte_vokabelkarten):
    """Konvertiert alte Vokabelkarten zur neuen Struktur."""
    neue_vokabelkarten = []
    for karte in alte_vokabelkarten:
        if isinstance(karte.lerneinheit, le_alt.LerneinheitChinesisch):
            if not karte.lerneinheit.eintrag.startswith("ChinEint"):
                neue_karte = vk.Vokabelkarte(
                    lerneinheit=convert_lerneinheit_chinesisch(karte.lerneinheit),
                    lernstats=karte.lernstats,
                    erzeugt=karte.erzeugt,
                    status=karte.status
                )
                neue_vokabelkarten.append(neue_karte) if neue_karte is not None else None
    return neue_vokabelkarten


def konvertiere_vokabelboxen(alte_vokabelboxen):
    """Konvertiert alte Vokabelboxen zur neuen Struktur."""
    neue_vokabelboxen = []
    for box in alte_vokabelboxen:
        neue_box = vb.Vokabelbox(
            titel=box.titel,
            lernklasse=box.lernklasse,
            selektor=box.selektor,
            aktuelle_frage=box.aktuelleFrage
        )
        neue_vokabelboxen.append(neue_box)
    return neue_vokabelboxen


def main():
    # Pfade zu alten Dateien
    alter_kartenpfad = "daten/vokabelkarten.data"
    alter_boxenpfad = "daten/vokabelboxen.data"

    # Pfade zu neuen Dateien
    neuer_kartenpfad = "daten/data/vokabelkarten.JSON"
    neuer_boxenpfad = "daten/data/vokabelboxen.JSON"

    # Laden der alten Daten
    alte_vokabelkarten = lade_pickle_datei(alter_kartenpfad)
    alte_vokabelboxen = lade_pickle_datei(alter_boxenpfad)

    # Konvertieren der Daten
    neue_vokabelkarten = konvertiere_vokabelkarten(alte_vokabelkarten)
    neue_vokabelboxen = konvertiere_vokabelboxen(alte_vokabelboxen)
    print(f"Karten: {len(neue_vokabelkarten)} Boxe: {len(neue_vokabelboxen)}")

    # Erstelle Repos zum Speichern und fuege die Daten hinzu.
    vokabelkarten_repo = InMemoryVokabelkartenRepository(dateiname=neuer_kartenpfad,
                                                         verzeichnis="",
                                                         vokabelkarten=neue_vokabelkarten,
                                                         speicher_methode=JSONDateiformatVokabelkarte)
    vokabelboxen_repo = InMemeoryVokabelboxRepository(dateiname=neuer_boxenpfad,
                                                      speicher_methode=JSONDateiformatVokabelbox)
    vokabelboxen_repo.vokabelboxen = neue_vokabelboxen

    # Speichern als JSON
    vokabelkarten_repo.speichern()
    vokabelboxen_repo.speichern()

    print(f"Konvertierung abgeschlossen! Neue Dateien gespeichert in '{neuer_kartenpfad}' und '{neuer_boxenpfad}'.")


if __name__ == "__main__":
    main()
