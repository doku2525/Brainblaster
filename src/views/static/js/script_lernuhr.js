import { ISOalsDatum, ISOalsUhrzeit } from "./modules/datumUndZeit.js";

let startUndKalkzeitVeraendert = false;

// Funktion zum Senden der Kommandos. Wird vom command_builder-Funktionen aufgerufen.
function sende_kommando(cmd) {
    fetch(cmd)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        })
        .then(data => {
            // data enthaelt die neue gerenderte HTML-Seite.
            // Schreibe data in ein dummy-div und extrahiere das meta-Element.
            // Setze die neuen Werte fuer die Kalender- und die Uhr-Objekte wie beim initialisieren
            if (startUndKalkzeitVeraendert = true) {    // Die if Abfrage ist vermutlich unnoetig
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = data;
                const metaElement = $(tempDiv).find('#startwerte');
                initializeKalenderUndUhrElement(metaElement.data());
                startUndKalkzeitVeraendert = false;
            }
        })
        .catch(error => {
            console.error('Fehler beim Senden:', error);
        });
}

// Ermittle den ausgewaehlten Radiobutton der Modus-Buttons und liefer den in value gespeicherten Wert
function getCheckedRadioButtonValue() {
    // Hole alle Radiobuttons mit dem Namen "modus"
    const radioButtons = document.getElementsByName("modus");
    // Iteriere über alle Radiobuttons
    for (let i = 0; i < radioButtons.length; i++) {
        if (radioButtons[i].checked) {
            // Wenn der Button ausgewählt ist, gib seinen Wert zurück und Disable unmoegliche Optionen.
            if (radioButtons[i].id === 'modus_pause_button') {
                document.getElementById('modus_echt_button').disabled = true;
                document.getElementById('modus_label_echt').style.textDecoration = "line-through";}
            if (radioButtons[i].id === 'modus_echt_button') {
                document.getElementById('modus_pause_button').disabled = true;
                document.getElementById('modus_label_pause').style.textDecoration = "line-through";}
            if (radioButtons[i].id === 'modus_laeuft_button') {
                document.getElementById('modus_pause_button').disabled = false;
                document.getElementById('modus_label_pause').style.textDecoration = "none";
                document.getElementById('modus_echt_button').disabled = false;
                document.getElementById('modus_label_echt').style.textDecoration = "none";}
            return radioButtons[i].value;
        }
    }
    // Wenn kein Button ausgewählt ist, gib einen Standardwert oder null zurück
    return null; // Oder einen anderen Standardwert
}

// Die Funktionen zum Bauen der Kommandos fuer den Listener
// Fuer kalkulations_zeit und start_zeit
function cmd_build_zeit(feldId, parameter) {
    const datum = document.getElementById('date_' + feldId + '_datum').value;
    const uhrzeit = document.getElementById('time_' + feldId + '_uhrzeit').value;
    const cmd = `/kommando/${parameter}=${datum} ${uhrzeit}`;
    console.log('Kommando gebaut: ', cmd);
    return cmd
}

// Fuer tempo
function cmd_build_tempo() {
    const wert = document.getElementById('tempo_wert').value;
    console.log('Tempo Wert: ', wert);
    const kommastellen = document.getElementById('tempo_kommastellen').value;
    console.log('Tempo Kommastelle: ', kommastellen);
    document.getElementById('tempo_wert_value').textContent = wert;
    document.getElementById('tempo_kommastellen_value').textContent = kommastellen;
    const neuerWert = Number(wert) + Number(kommastellen);
    document.getElementById('neuer_tempo_wert').textContent = neuerWert;
    const cmd = `/kommando/ct${neuerWert}`;
    console.log('Kommando gebaut: ', cmd);
    return cmd
}

function cmd_build_modus() {
    const wert = getCheckedRadioButtonValue();
    const cmd = `/kommando/c${wert}`;
    console.log('Kommando gebaut: ', cmd);
    return cmd
}


// JavaScript-Code zur dynamischen Anpassung der Benutzeroberfläche
function fetchData() {
    fetch('/get_aktuelle_und_neue_uhrzeit')
        .then(response => response.json())
        .then(data => {
            document.getElementById('aktuelle_uhrzeit').textContent = data.aktuelle_uhrzeit;
            document.getElementById('neue_uhrzeit').textContent = data.neue_uhrzeit;
            // TODO Die Ausgabe als JSON in testausgabe sollte irgendwann entfernt werden.
            // document.getElementById('neue_uhr').textContent = JSON.stringify(data.neue_uhr);
        })
        .catch(error => {
            console.error('Fehler beim Abrufen der Uhrzeit:', error);
        });
}

// Funktionen fuer die Buttons
function speicherLernuhr() { window.location.href = '/index?lernuhr=mit_speichern';}
function verwerfeLernuhr() { window.location.href = '/index?lernuhr=ohne_speichern';}
function calibriereLernuhr() {
    // Die neuen Daten weren in sendeKommando dem Kalnder- und Uhr-Element zugwiesen
    sende_kommando('/kommando/cc');
    startUndKalkzeitVeraendert = true;   // Flag, die in sendeKommando() abgefragt wird
}
function resetLernuhr() {
    // Die neuen Daten weren in sendeKommando dem Kalnder- und Uhr-Element zugwiesen
    sende_kommando('/kommando/cr');
    startUndKalkzeitVeraendert = true;   // Flag, die in sendeKommando() abgefragt wird
}

// Buttonfunktionen im Global-Space registrieren
window.speicherLernuhr = speicherLernuhr;
window.verwerfeLernuhr = verwerfeLernuhr;
window.calibriereLernuhr = calibriereLernuhr;
window.resetLernuhr = resetLernuhr;

// Markiere aktuellen Radiobutton beim Laden der Seite
function setRadioByData(data) {
    // Hole das Element mit der passenden ID
    const radio = document.getElementById('modus_' + data.toLowerCase() + '_button');

    // Überprüfe, ob das Element gefunden wurde
    if (radio) {
        // Setze den Radiobutton als ausgewählt
        radio.checked = true;
        // Disable unmoegliche Kombinationen
        const dummy = getCheckedRadioButtonValue();

    } else {
        console.error('Kein Radiobutton mit der ID gefunden:', 'modus-' + data.toLowerCase() + '-button');
    }
}

function registerListener() {
        // Die Listener starten
        document.getElementById('date_kalkulations_zeit_datum').addEventListener('change', () => {
            const cmd = cmd_build_zeit('kalkulations_zeit', 'ck');
            sende_kommando(cmd)});
        document.getElementById('time_kalkulations_zeit_uhrzeit').addEventListener('change', () => {
            const cmd = cmd_build_zeit('kalkulations_zeit', 'ck');
            sende_kommando(cmd)});
        document.getElementById('date_start_zeit_datum').addEventListener('change', () => {
            const cmd = cmd_build_zeit('start_zeit', 'cs');
            sende_kommando(cmd)});
        document.getElementById('time_start_zeit_uhrzeit').addEventListener('change', () => {
            const cmd = cmd_build_zeit('start_zeit', 'cs');
            sende_kommando(cmd)});
        document.getElementById('tempo_wert').addEventListener('change', () => {
            const cmd = cmd_build_tempo();
            sende_kommando(cmd)});
        document.getElementById('tempo_kommastellen').addEventListener('change', () => {
            const cmd = cmd_build_tempo();
            sende_kommando(cmd)});
        document.getElementById('modus_echt_button').addEventListener('change', () => {
            const cmd = cmd_build_modus();
            sende_kommando(cmd)});
        document.getElementById('modus_laeuft_button').addEventListener('change', () => {
            const cmd = cmd_build_modus();
            sende_kommando('/kommando/cpe');
            // Wenn der Timeout zu kurz ist, wird das Kommando vom Server nicht verarbeitet
            setTimeout(function() {sende_kommando(cmd)}, 500);});
        document.getElementById('modus_pause_button').addEventListener('change', () => {
            const cmd = cmd_build_modus();
            sende_kommando('/kommando/cpb');
            // Wenn der Timeout zu kurz ist, wird das Kommando vom Server nicht verarbeitet
            setTimeout(function() {sende_kommando(cmd);}, 500)});
}

function initializeKalenderUndUhrElement(daten) {
    document.getElementById('date_kalkulations_zeit_datum').value = ISOalsDatum(daten.kalkulations_zeit);
    document.getElementById('time_kalkulations_zeit_uhrzeit').value = ISOalsUhrzeit(daten.kalkulations_zeit);
    document.getElementById('date_start_zeit_datum').value = ISOalsDatum(daten.start_zeit);
    document.getElementById('time_start_zeit_uhrzeit').value = ISOalsUhrzeit(daten.start_zeit);
}

function initializeElemente() {
    // Lese die Werte aus Meta-Element in <head>
    let startwerte = $('#startwerte').data();
    var aktuellerModus = startwerte.modus;
    setRadioByData(aktuellerModus);
    document.getElementById('tempo_wert').value = startwerte.tempo_wert;
    document.getElementById('tempo_kommastellen').value = startwerte.tempo_kommastellen;
    document.getElementById('tempo_wert_value').textContent = startwerte.tempo_wert;
    document.getElementById('tempo_kommastellen_value').textContent = startwerte.tempo_kommastellen;
    document.getElementById('neuer_tempo_wert').textContent = Number(startwerte.tempo_wert) +
                                                              Number(startwerte.tempo_kommastellen);
    initializeKalenderUndUhrElement(startwerte)
}

initializeElemente();
registerListener();
setInterval(fetchData, 1000);