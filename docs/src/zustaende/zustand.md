# Zustandsklassen

Dieses Dokument beschreibt die verschiedenen Zustandsklassen, die im Vokabeltrainer verwendet werden. Jede Zustandsklasse repräsentiert einen bestimmten Zustand im Programmfluss und bietet Methoden zur Verarbeitung von Benutzereingaben.

Momentan sind folgende **konkrete Zustände** implementiert:

- ZustandStart
- ZustandENDE
- ZustandVeraenderLernuhr
- ZustandVokabelTesten (Basisklasse fuer Pruefen, Lernen, Neue)
- ZustandVokabelPruefen
- ZustandVokabelLernen
- ZustandVokabelNeue
- ZustandZeigeVokabelliste (Basisklasse fuer Komplett, Lernen, Neue)
- ZustandZeigeVokabellisteKomplett
- ZustandZeigeVokabellisteLernen
- ZustandZeigeVokabellisteNeue
---

## Zustand (Basisklasse)

Die Basisklasse `Zustand` ist eine abstrakte Klasse, die von allen anderen Zustandsklassen erweitert wird. Sie definiert die grundlegenden Attribute und Methoden, die für alle Zustände relevant sind.

### Attribute
- **parent**: Der übergeordnete Zustand (falls vorhanden).
- **child**: Eine Liste von untergeordneten Zuständen.
- **beschreibung**: Eine Beschreibung des Zustands.
- **titel**: Der Titel des Zustands.
- **kommandos**: Eine Liste von verfügbaren Kommandos.
- **aktuelle_zeit**: Die aktuelle Zeit im ISO-Format.

### Methoden
- **`verarbeite_userinput(index_child: str) -> ZustandReturnValue`**:
  - **Beschreibung**: Verarbeitet die Benutzereingabe und gibt den nächsten Zustand zurück.
  - **Parameter**: `index_child` – Die Benutzereingabe.
  - **Rückgabewert**: Ein `ZustandReturnValue`-Objekt, das den nächsten Zustand und ein optionales Kommando enthält.

- **`update_zeit(neue_zeit_im_iso_format: str)`**:
  - **Beschreibung**: Aktualisiert die `aktuelle_zeit` des Zustands.
  - **Parameter**: `neue_zeit_im_iso_format` – Die neue Zeit im ISO-Format.
  - **Rückgabewert**: Der aktualisierte Zustand.

#### Hilfsmethoden
- **`position_zustand_in_child_mit_namen(klassen_name: str) -> str`**:
  - **Beschreibung**: Gibt die Position des Zustands in der `child`-Liste zurück, der den angegebenen Klassennamen hat.
  - **Parameter**: `klassen_name` – Der Name der Zustandsklasse.
  - **Rückgabewert**: Die Position als String (leer, wenn nicht gefunden).

---

## ZustandENDE

Die Klasse `ZustandENDE` repräsentiert den Endzustand des Programms.

### Attribute
- **titel**: `'ENDE'`
- **beschreibung**: `'Beende Programm'`

---

## ZustandBoxinfo

Die Klasse `ZustandBoxinfo` zeigt Informationen über die aktuelle Vokabelbox an.

### Attribute
- **info**: Ein Dictionary mit Informationen über die Vokabelbox.
- **aktuelle_frageeinheit**: Die aktuelle Frageeinheit.
- **box_titel**: Der Titel der Vokabelbox.
- **titel**: `'Zustand 2'`
- **beschreibung**: `'Zustand 2, Zeigt die Boxinfos der aktuellen Box an.'`
- **child**: Eine Liste von untergeordneten Zuständen.
- **kommandos**: `('+', '-', '=')`

### Methoden
- **`verarbeite_userinput(index_child: str) -> ZustandReturnValue`**:
  - **Beschreibung**: Verarbeitet die Benutzereingabe, um die aktuelle Frageeinheit zu ändern.
  - **Parameter**: `index_child` – Die Benutzereingabe.
  - **Rückgabewert**: Ein `ZustandReturnValue`-Objekt.

---

## ZustandStart

Die Klasse `ZustandStart` repräsentiert den Startzustand des Programms.

### Attribute
- **liste**: Eine Liste von Vokabelbox-Titeln.
- **aktueller_index**: Der Index der aktuellen Vokabelbox.
- **titel**: `'Zustand 1'`
- **beschreibung**: `'Zustand 1, der die aktuelle Box und den Namen der aktuellen Box anzeigt.'`
- **child**: Eine Liste von untergeordneten Zuständen (standardmäßig `ZustandENDE`).
- **kommandos**: `('+', '-', '=', 's')`

### Methoden
- **`verarbeite_userinput(index_child: str) -> ZustandReturnValue`**:
  - **Beschreibung**: Verarbeitet die Benutzereingabe, um die aktuelle Vokabelbox zu ändern oder Daten zu speichern.
  - **Parameter**: `index_child` – Die Benutzereingabe.
  - **Rückgabewert**: Ein `ZustandReturnValue`-Objekt.

---

## ZustandVeraenderLernuhr

Die Klasse `ZustandVeraenderLernuhr` ermöglicht das Ändern der Lernuhr-Einstellungen.

### Attribute
- **titel**: `'ZustandStelleUhr'`
- **beschreibung**: `'Zustand, zum Stellen der Uhr.'`
- **child**: Eine Liste von untergeordneten Zuständen.
- **kommandos**: `('s', 'k', 't', 'z', 'p', 'r', 'c')`
- **neue_uhr**: Die neue Lernuhr-Einstellung.

### Methoden
- **`verarbeite_userinput(index_child: str) -> ZustandReturnValue`**:
  - **Beschreibung**: Verarbeitet die Benutzereingabe, um die Lernuhr zu ändern.
  - **Parameter**: `index_child` – Die Benutzereingabe.
  - **Rückgabewert**: Ein `ZustandReturnValue`-Objekt.

---

## ZustandVokabelTesten

Die Klasse `ZustandVokabelTesten` ist die Basisklasse für alle Testzustände.

### Attribute
- **input_liste**: Eine Liste von Vokabelkarten, die getestet werden sollen.
- **output_liste**: Eine Liste von Vokabelkarten, die bereits getestet wurden.
- **aktuelle_frageeinheit**: Die aktuelle Frageeinheit.
- **wiederholen**: Gibt an, ob falsch beantwortete Karten wiederholt werden sollen.
- **titel**: `'Zustand Testen'`
- **beschreibung**: `'Zustand Testen, führt die Tests aus und verarbeitet Antworten.'`
- **kommandos**: `('a', 'e')`

### Methoden
- **`verarbeite_userinput(index_child: str) -> ZustandReturnValue`**:
  - **Beschreibung**: Verarbeitet die Benutzereingabe, um Vokabelkarten zu testen.
  - **Parameter**: `index_child` – Die Benutzereingabe.
  - **Rückgabewert**: Ein `ZustandReturnValue`-Objekt.

---

## ZustandVokabelPruefen

Die Klasse `ZustandVokabelPruefen` erweitert `ZustandVokabelTesten` und ist spezialisiert auf das Prüfen von Vokabeln.

### Attribute
- **titel**: `'Zustand Pruefen'`
- **beschreibung**: `'Zustand Pruefen, führt die Pruefen-Tests aus und verarbeitet Antworten.'`

---

## ZustandVokabelLernen

Die Klasse `ZustandVokabelLernen` erweitert `ZustandVokabelTesten` und ist spezialisiert auf das Lernen von Vokabeln.

### Attribute
- **titel**: `'Zustand Lernen'`
- **beschreibung**: `'Zustand Lernen, führt die Lernen-Tests aus und verarbeitet Antworten.'`

---

## ZustandVokabelNeue

Die Klasse `ZustandVokabelNeue` erweitert `ZustandVokabelTesten` und ist spezialisiert auf das Testen neuer Vokabeln.

### Attribute
- **titel**: `'Zustand Neue'`
- **beschreibung**: `'Zustand Neue, führt die Neue-Tests aus und verarbeitet Antworten.'`

---

## ZustandZeigeVokabelliste

Die Klasse `ZustandZeigeVokabelliste` zeigt eine Liste von Vokabelkarten an.

### Attribute
- **titel**: `'Zustand Zeige Vokabelliste'`
- **beschreibung**: `'Zustand Zeige Vokabelliste, die wesentlichen Daten der Karten als Liste.'`
- **kommandos**: `('e',)`
- **liste**: Eine Liste von `DisplayPatternVokabelkarte`-Objekten.
- **modus**: Der Modus der Liste (z. B. `'komplett'`, `'lernen'`, `'neue'`).
- **frageeinheit_titel**: Der Titel der aktuellen Frageeinheit.
- **vokabelbox_titel**: Der Titel der aktuellen Vokabelbox.

### Methoden
- **`erzeuge_aus_vokabelliste(vokabelliste: list[Vokabelkarte]) -> cls`**:
  - **Beschreibung**: Erstellt eine Instanz der Klasse aus einer Liste von Vokabelkarten.
  - **Parameter**: `vokabelliste` – Die Liste der Vokabelkarten.
  - **Rückgabewert**: Eine Instanz der Klasse.

---

## ZustandZeigeVokabellisteKomplett

Die Klasse `ZustandZeigeVokabellisteKomplett` zeigt eine vollständige Liste von Vokabelkarten an.

### Attribute
- **modus**: `'komplett'`

---

## ZustandZeigeVokabellisteLernen

Die Klasse `ZustandZeigeVokabellisteLernen` zeigt eine Liste von Vokabelkarten an, die zum Lernen vorgesehen sind.

### Attribute
- **modus**: `'lernen'`

---

## ZustandZeigeVokabellisteNeue

Die Klasse `ZustandZeigeVokabellisteNeue` zeigt eine Liste von neuen Vokabelkarten an.

### Attribute
- **modus**: `'neue'`