from src.repositories.vokabelkarten_repository import InMemoryVokabelkartenRepository, JSONDateiformatVokabelkarte
from src.repositories.vokabelbox_repository import InMemeoryVokabelboxRepository, JSONDateiformatVokabelbox
from src.classes.vokabeltrainermodell import VokabeltrainerModell
# from src.classes.configurator import config
from src.classes.vokabelkarte import Vokabelkarte
from src.classes.lernuhr import Lernuhr
import src.utils.utils_io as u_io
from dataclasses import replace


def is_vokabelliste_sorted(liste: list[Vokabelkarte]) -> bool:
    return all(a.lerneinheit.erzeugt <= b.lerneinheit.erzeugt for a, b in zip(liste, liste[1:]))


def is_non_unique_in_list(karten_liste: list[Vokabelkarte]) -> bool:
    list_of_ids = [karte.lerneinheit.erzeugt for karte in karten_liste]
    return len(list_of_ids) > len(set(list_of_ids))


def update_erzeugt_wert(karte: Vokabelkarte, index) -> Vokabelkarte:
    lerneinheit = replace(karte.lerneinheit, erzeugt=karte.erzeugt + index)
    return replace(replace(karte, erzeugt=karte.erzeugt + index), lerneinheit=lerneinheit)


def erzeuge_unique_ids(karten_liste: list[Vokabelkarte]) -> list[tuple[Vokabelkarte, Vokabelkarte]]:
    """Die Funtkion sollte nur auf Listen, die nicht unique IDs beinhalten, ausgefuehrt werden, da sonst die IDs
    nur sinnlos aufaddiert werden.
    Deshalb sollte diese Funktion nur in einem if-Zweig der Funktion
    is_non_unique_in_list(karten_liste) ausgefuert werden. Siehe main()"""
    if is_vokabelliste_sorted(karten_liste):
        result = list(((karte, update_erzeugt_wert(karte, index))
                       for index, karte
                       in enumerate(karten_liste)))
        result_list = [karte for _, karte in result]
        print(f"Unique IDS erzeugt ...")
        print(f"Anzahl der Vokabelkarten in Result = {len(result_list)}")
        print(f"Anzahl IDs in Result = {len(set([karte.erzeugt for karte in result_list]))}")
        print(f"Anzahl IDs in Result Lerneinheit = {len(set([karte.lerneinheit.erzeugt for karte in result_list]))}")
        print(f"Es gibt nicht-unique IDs = {is_non_unique_in_list(result_list)}")
        print(f"Alle erzeugt in Karte und Lerneinheit identisch = {all(karte.erzeugt == karte.lerneinheit.erzeugt for karte in result_list)}")
        print(f"{result[0][1].erzeugt - result[0][0].erzeugt = } {result[-1][1].erzeugt - result[-1][0].erzeugt = }")
    return result


def main():
    vokabelkarten_repo = InMemoryVokabelkartenRepository(dateiname=f"../../daten/data/vokabelkarten.JSON",
                                                         verzeichnis='', speicher_methode=JSONDateiformatVokabelkarte)
    vokabelkarten_repo.laden()
    vokabelkarten = vokabelkarten_repo.vokabelkarten

    print(f"Anzahl der Vokabelkarten = {len(vokabelkarten)}")
    print(f"Anzahl IDs in Karte = {len(set([karte.erzeugt for karte in vokabelkarten]))}")
    print(f"Es gibt nicht-unique IDs = {is_non_unique_in_list(vokabelkarten)}")
    print(f"Anzahl IDs in Lerneinheit = {len(set([karte.lerneinheit.erzeugt for karte in vokabelkarten]))}")
    print(f"Alle erzeugt in Karte und Lerneinheit identisch = {all(karte.erzeugt == karte.lerneinheit.erzeugt for karte in vokabelkarten)}")
    print(f"Vokabelkarten nach Erzeugung soriert = {is_vokabelliste_sorted(vokabelkarten)}")
    print(f"Starte Prozess ...")
    if is_non_unique_in_list(vokabelkarten):
        result = erzeuge_unique_ids(vokabelkarten)
        print(f"Update Repositiory ...")
        [vokabelkarten_repo.replace_karte(alt, neu) for alt, neu in result]
        print(f"Teste Repositiory ...")
        print(f"Anzahl der Vokabelkarten = {len(vokabelkarten)}")
        print(f"Anzahl IDs in Lerneinheit = {len(set([karte.lerneinheit.erzeugt for karte in vokabelkarten_repo.vokabelkarten]))}")
        print(f"Anzahl IDs = {len(set([karte.erzeugt for karte in vokabelkarten_repo.vokabelkarten]))}")
        print(f"Es gibt nicht-unique IDs = {is_non_unique_in_list(vokabelkarten_repo.vokabelkarten)}")
        print(f"Speicher Repo")
        vokabelkarten_repo.speichern()
    else:
        print(f"Liste ist bereits unique")


# TODO Testen, ob prozess wirklich notwendig ist, also wirklich alle Unique sind.
if __name__ == '__main__':
    main()
