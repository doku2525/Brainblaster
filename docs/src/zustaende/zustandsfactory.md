# ZustandsFactory

Die `ZustandsFactory` ist eine zentrale Klasse, die für die Erstellung und Aktualisierung von Zuständen in einem Vokabeltrainer verantwortlich ist. Sie verwendet verschiedene Zustandsklassen, um den aktuellen Zustand des Vokabeltrainers zu repräsentieren und zu verwalten.

## Attribute

- **modell**: Eine Instanz von `VokabeltrainerModell`, die das aktuelle Modell des Vokabeltrainers repräsentiert.
- **uhr**: Eine Instanz von `Lernuhr`, die die aktuelle Zeit verwaltet.
- **info_manager**: Eine Instanz von `InfoManager`, die Informationen über die Vokabelboxen verwaltet.
---
## Methoden
Die Methoden lassen sich in drei Kategorien unterteilen.
- [Hilfsmethoden](#Hilfsmethoden): Mappinglisten, getter()-artige Methoden
- [Buildermethoden](#Buildermethoden): Erstellen die Zustände
- [Updatemethoden](#Updatemethoden): Updaten die Zuständen
---
<a><a id="hilfsmethoden"></a>
### Hilfsmethoden

#### `zustaende_ohne_update() -> list[Type[Zustand]]`
- **Beschreibung**: Gibt eine Liste von Zustandsklassen zurück, die nicht aktualisiert werden müssen.
- **Rückgabewert**: Eine Liste von Zustandsklassen (`ZustandVeraenderLernuhr`, `ZustandVokabelPruefen`, `ZustandVokabelLernen`, `ZustandVokabelNeue`).

#### `start_zustand() -> ZustandStart`
- **Beschreibung**: Erstellt und gibt den Startzustand (`ZustandStart`) zurück.
- **Rückgabewert**: Eine Instanz von `ZustandStart`.

#### `end_zustand() -> Type[Zustand]`
- **Beschreibung**: Gibt den Endzustand (`ZustandENDE`) zurück.
- **Rückgabewert**: Die Klasse `ZustandENDE`.

---
<a><a id="buildermethoden"></a>
### Buildermethoden

#### `buildZustandStart(zustand: ZustandStart) -> ZustandStart`
- **Beschreibung**: Erstellt den Startzustand mit den aktuellen Werten aus dem Modell und der Uhr.
- **Parameter**: `zustand` – Der aktuelle Startzustand.
- **Rückgabewert**: Eine aktualisierte Instanz von `ZustandStart`.

#### `buildZustandBoxinfo(zustand: ZustandBoxinfo) -> ZustandBoxinfo`
- **Beschreibung**: Erstellt den Zustand `ZustandBoxinfo` mit Informationen über die aktuelle Vokabelbox.
- **Parameter**: `zustand` – Der aktuelle Zustand `ZustandBoxinfo`.
- **Rückgabewert**: Eine aktualisierte Instanz von `ZustandBoxinfo`.

#### `buildZustandVeraenderLernuhr(zustand: ZustandVeraenderLernuhr) -> ZustandVeraenderLernuhr`
- **Beschreibung**: Aktualisiert den Zustand `ZustandVeraenderLernuhr` mit der aktuellen Zeit.
- **Parameter**: `zustand` – Der aktuelle Zustand `ZustandVeraenderLernuhr`.
- **Rückgabewert**: Eine aktualisierte Instanz von `ZustandVeraenderLernuhr`.

#### `buildZustandVokabelTesten(zustand: ZustandVokabelTesten, filter_liste: list, vokabel_liste: list = None) -> ZustandVokabelTesten`
- **Beschreibung**: Basis-Funktion, die den Zustand `ZustandVokabelTesten` zurückgibt. Wird von den spezifischen Funktionen für Prüfen, Lernen und Neue Vokabeln aufgerufen.
- **Parameter**:
  - `zustand` – Der aktuelle Zustand `ZustandVokabelTesten`.
  - `filter_liste` – Eine Liste von Filtern, die auf die Vokabeln angewendet werden.
  - `vokabel_liste` – Eine Liste von Vokabeln (optional).
- **Rückgabewert**: Eine aktualisierte Instanz von `ZustandVokabelTesten`.

#### `buildZustandVokabelPruefen(zustand: ZustandVokabelPruefen) -> ZustandVokabelPruefen`
- **Beschreibung**: Erstellt den Zustand `ZustandVokabelPruefen` mit den gefilterten Vokabeln zum Prüfen.
- **Parameter**: `zustand` – Der aktuelle Zustand `ZustandVokabelPruefen`.
- **Rückgabewert**: Eine aktualisierte Instanz von `ZustandVokabelPruefen`.

#### `buildZustandVokabelLernen(zustand: ZustandVokabelLernen) -> ZustandVokabelLernen`
- **Beschreibung**: Erstellt den Zustand `ZustandVokabelLernen` mit den gefilterten Vokabeln zum Lernen.
- **Parameter**: `zustand` – Der aktuelle Zustand `ZustandVokabelLernen`.
- **Rückgabewert**: Eine aktualisierte Instanz von `ZustandVokabelLernen`.

#### `buildZustandVokabelNeue(zustand: ZustandVokabelNeue) -> ZustandVokabelNeue`
- **Beschreibung**: Erstellt den Zustand `ZustandVokabelNeue` mit den gefilterten neuen Vokabeln.
- **Parameter**: `zustand` – Der aktuelle Zustand `ZustandVokabelNeue`.
- **Rückgabewert**: Eine aktualisierte Instanz von `ZustandVokabelNeue`.

#### `buildZustandZeigeVokabelliste(zustand: ZustandZeigeVokabelliste, modus: str, liste: list) -> ZustandZeigeVokabelliste`
- **Beschreibung**: Erstellt den Zustand `ZustandZeigeVokabelliste` mit der angegebenen Liste von Vokabeln.
- **Parameter**:
  - `zustand` – Der aktuelle Zustand `ZustandZeigeVokabelliste`.
  - `modus` – Der Modus, in dem die Vokabelliste angezeigt wird.
  - `liste` – Die Liste der Vokabeln.
- **Rückgabewert**: Eine aktualisierte Instanz von `ZustandZeigeVokabelliste`.

#### `buildZustandZeigeVokabellisteKomplett(zustand: ZustandZeigeVokabellisteKomplett) -> ZustandZeigeVokabellisteKomplett`
- **Beschreibung**: Erstellt den Zustand `ZustandZeigeVokabellisteKomplett` mit der kompletten Liste von Vokabeln.
- **Parameter**: `zustand` – Der aktuelle Zustand `ZustandZeigeVokabellisteKomplett`.
- **Rückgabewert**: Eine aktualisierte Instanz von `ZustandZeigeVokabellisteKomplett`.

#### `buildZustandZeigeVokabellisteLernen(zustand: ZustandZeigeVokabellisteLernen) -> ZustandZeigeVokabellisteLernen`
- **Beschreibung**: Erstellt den Zustand `ZustandZeigeVokabellisteLernen` mit der Liste von Vokabeln zum Lernen.
- **Parameter**: `zustand` – Der aktuelle Zustand `ZustandZeigeVokabellisteLernen`.
- **Rückgabewert**: Eine aktualisierte Instanz von `ZustandZeigeVokabellisteLernen`.

#### `buildZustandZeigeVokabellisteNeue(zustand: ZustandZeigeVokabellisteNeue) -> ZustandZeigeVokabellisteNeue`
- **Beschreibung**: Erstellt den Zustand `ZustandZeigeVokabellisteNeue` mit der Liste von neuen Vokabeln.
- **Parameter**: `zustand` – Der aktuelle Zustand `ZustandZeigeVokabellisteNeue`.
- **Rückgabewert**: Eine aktualisierte Instanz von `ZustandZeigeVokabellisteNeue`.
---
<a><a id="Updatemethoden"></a>
## Updatemethoden

#### `update_zustand(alter_zustand: Zustand) -> Zustand`
- **Beschreibung**: Aktualisiert den Zustand basierend auf dem aktuellen Zustand und ruft die entsprechenden Builder-Funktionen auf.
- **Parameter**: `alter_zustand` – Der aktuelle Zustand, der aktualisiert werden soll.
- **Rückgabewert**: Der aktualisierte Zustand.

#### `update_frageeinheit(zustand: Zustand) -> Zustand`
- **Beschreibung**: Aktualisiert die Frageeinheit in den Zuständen, die `ZustandVokabelTesten` sind.
- **Parameter**: `zustand` – Der aktuelle Zustand.
- **Rückgabewert**: Der aktualisierte Zustand.

#### `update_with_childs(zustand: Zustand) -> Zustand`
- **Beschreibung**: Aktualisiert den Zustand und seine Kind-Zustände, falls notwendig.
- **Parameter**: `zustand` – Der aktuelle Zustand.
- **Rückgabewert**: Der aktualisierte Zustand.