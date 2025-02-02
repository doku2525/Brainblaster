# VokabeltrainerController

Die Klasse `VokabeltrainerController` ist das zentrale Steuerungselement des Vokabeltrainers. Sie verwaltet den Zustand des Programms, verarbeitet Benutzereingaben und koordiniert die Interaktion zwischen dem Modell, der Uhr, dem InfoManager und der View.

---

## Attribute

- **modell**: Eine Instanz von `VokabeltrainerModell`, die das Datenmodell des Vokabeltrainers repräsentiert.
- **info_manager**: Eine Instanz von `InfoManager`, die Informationen über die Vokabelboxen und -karten verwaltet.
- **uhr**: Eine Instanz von `Lernuhr`, die die aktuelle Zeit verwaltet.
- **aktueller_zustand**: Der aktuelle Zustand des Vokabeltrainers.
- **view_observer**: Eine Instanz von `ObserverManager`, die für die Aktualisierung der View verantwortlich ist.
- **event_manager**: Eine Instanz von `EventManager`, die Ereignisse im System verwaltet.
- **cmd**: Der aktuelle Befehl, der vom Benutzer eingegeben wurde.
- **task_manager**: Eine Instanz von `TaskManager`, die Hintergrundaufgaben verwaltet.

---

## Methoden
### Initializierung
- **`__init__(self, modell: VokabeltrainerModell, uhr: Lernuhr, view_observer: ObserverManager, event_manager: EventManager, task_manager: TaskManager = None)`**:
  - **Beschreibung**: Initialisiert den Controller mit den notwendigen Komponenten.
  - **Parameter**:
    - `modell`: Das Datenmodell des Vokabeltrainers.
    - `uhr`: Die Lernuhr.
    - `view_observer`: Der ObserverManager für die View.
    - `event_manager`: Der EventManager für die Ereignisverwaltung.
    - `task_manager`: Der TaskManager für Hintergrundaufgaben (optional).

### Hilfsfunktion
- **`__task_funktion_erzeuge_infos(self, zeit: int) -> Callable`**:
  - **Beschreibung**: Hilfsfunktion, die eine Callback-Funktion für den TaskManager erstellt, um die Infos zu aktualisieren.
  - **Parameter**: `zeit` – Die aktuelle Zeit.
  - **Rückgabewert**: Eine Callback-Funktion, die den `InfoManager` aktualisiert.

---

### Methoden zum Veraendern der Parameter
- **`update_uhr(self, neue_uhr: Lernuhr) -> None`**:
  - **Beschreibung**: Aktualisiert die Lernuhr und den `InfoManager`.
  - **Parameter**: `neue_uhr` – Die neue Lernuhr.
  - **Rückgabewert**: Keiner.


- **`update_modell_aktueller_index(self, neuer_index: int) -> None`**:
  - **Beschreibung**: Aktualisiert den Index der aktuellen Vokabelbox im Modell.
  - **Parameter**: `neuer_index` – Der neue Index.
  - **Rückgabewert**: Keiner.


- **`update_modell_aktuelle_frageeinheit(self, neue_frageeinheit: str) -> None`:**
  - **Beschreibung**: Aktualisiert die aktuelle Frageeinheit in der aktuellen Vokabelbox.
  - **Parameter**: `neue_frageeinheit` – Der Name der neuen Frageeinheit.
  - **Rückgabewert**: Keiner.


- **`__task_funktion_update_infos(self, karte_alt: Vokabelkarte, karte_neu: Vokabelkarte, zeit: int) -> Callable`**:
  - **Beschreibung**: Hilfsfunktion, die eine Callback-Funktion für den TaskManager erstellt, um die Infos für eine Vokabelkarte zu aktualisieren.
  - **Parameter**:
    - `karte_alt` – Die alte Vokabelkarte.
    - `karte_neu` – Die neue Vokabelkarte.
    - `zeit` – Die aktuelle Zeit.
  - **Rückgabewert**: Eine Callback-Funktion, die den `InfoManager` aktualisiert.


- **`update_vokabelkarte_statistik(self, karte: tuple[Vokabelkarte, Callable[[int], Vokabelkarte]]) -> None`**:
  - **Beschreibung**: Aktualisiert die Statistik einer Vokabelkarte und ersetzt die alte Karte durch die neue im Repository.
  - **Parameter**: `karte` – Ein Tupel aus der alten Vokabelkarte und einer Funktion, die die neue Karte erstellt.
  - **Rückgabewert**: Keiner.


- ** `speicher_daten_in_dateien(self)`**:
  - **Beschreibung**: Speichert die Daten des Vokabeltrainers in Dateien.
  - **Rückgabewert**: Keiner.

---
### controller Methoden
- **`execute_kommando(self, kommando_string: str) -> Zustand`**:
  - **Beschreibung**: Führt ein Kommando aus und aktualisiert den aktuellen Zustand.
  - **Parameter**: `kommando_string` – Der eingegebene Befehl.
  - **Rückgabewert**: Der aktualisierte Zustand.

- **`setze_cmd_str(self, cmd_str) -> None`**:
  - **Beschreibung**: Setzt den aktuellen Befehl und führt ihn aus.
  - **Parameter**: `cmd_str` – Der eingegebene Befehl.
  - **Rückgabewert**: Keiner.

- **`programm_loop(self)`**:
  - **Beschreibung**: Die Hauptschleife des Programms, die den Zustand des Vokabeltrainers verwaltet und die View aktualisiert.
  - **Rückgabewert**: Keiner.

---

## Ereignisse

Der Controller abonniert und veröffentlicht verschiedene Ereignisse über den `EventManager`:

- **NEUES_KOMMANDO**: Wird ausgelöst, wenn ein neuer Befehl eingegeben wird.
- **KOMMANDO_EXECUTED**: Wird ausgelöst, nachdem ein Befehl ausgeführt wurde.
- **LOOP_ENDE**: Wird am Ende jeder Schleifeniteration ausgelöst.
- **PROGRAMM_BENDET**: Wird ausgelöst, wenn das Programm beendet wird.

---

## Beispiel

Hier ist ein Beispiel, wie der Controller verwendet wird:

```python
# Initialisiere die notwendigen Komponenten
modell = VokabeltrainerModell()
uhr = Lernuhr()
view_observer = ObserverManager()
event_manager = EventManager()
task_manager = TaskManager()

# Erstelle den Controller
controller = VokabeltrainerController(modell, uhr, view_observer, event_manager, task_manager)

# Starte die Hauptschleife
controller.programm_loop()