
let startUndKalkzeitVeraendert = false;

function ISOalsDatum(datetimeString) {
    const dateRegex = /^\d{4}-\d{2}-\d{2}/;
    return datetimeString.match(dateRegex)[0];
}

function ISOalsUhrzeit(datetimeString) {
    const timeRegex = /\d{2}:\d{2}:\d{2}/;
    return datetimeString.match(timeRegex)[0];
}

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
            console.log('Erfolgreich gesendet:', data);
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
    const wert = getCheckedRadioButtonValue()
    const cmd = `/kommando/c${wert}`;
    console.log('Kommando gebaut: ', cmd);
    return cmd
}


// JavaScript-Code zur dynamischen Anpassung der Benutzeroberfläche
function fetchData() {
    fetch('/get_aktuelle_und_neue_uhrzeit')
        .then(response => response.json())
        .then(data => {
        // TODO Wenn reset() oder calibrate() dann setze Flag und Update hier die Kalender und Zeit objekte.
            document.getElementById('aktuelle_uhrzeit').textContent = data.aktuelle_uhrzeit;
            document.getElementById('neue_uhrzeit').textContent = data.neue_uhrzeit;
            if (startUndKalkzeitVeraendert) {   // Flag wird in den Funktionen fuer die Buttons verwendet
                const start_zeit = data.neue_uhr.start_zeit
                const kalk_zeit = data.neue_uhr.kalkulations_zeit
                document.getElementById('date_start_zeit_datum').value = ISOalsDatum(start_zeit)
                document.getElementById('time_start_zeit_uhrzeit').value = ISOalsUhrzeit(start_zeit)
                document.getElementById('date_kalkulations_zeit_datum').value = ISOalsDatum(kalk_zeit)
                document.getElementById('time_kalkulations_zeit_uhrzeit').value = ISOalsUhrzeit(kalk_zeit)
                startUndKalkzeitVeraendert = false;
            }
            document.getElementById('neue_uhr').textContent = JSON.stringify(data.neue_uhr);
            document.getElementById('testausgabe').textContent = data.neue_uhr.kalkulations_zeit;
        })
        .catch(error => {
            console.error('Fehler beim Abrufen der Uhrzeit:', error);
        });
}

// Funktionen fuer die Buttons
function speicherLernuhr() { window.location.href = '/index?lernuhr=mit_speichern';}
function verwerfeLernuhr() { window.location.href = '/index?lernuhr=ohne_speichern';}
function calibriereLernuhr() {
    sende_kommando('/kommando/cc');
    startUndKalkzeitVeraendert = true;   // Flag, die in fetchData() abgefragt wird
}
function resetLernuhr() {
    sende_kommando('/kommando/cr');
    startUndKalkzeitVeraendert = true;   // Flag, die in fetchData() abgefragt wird
}

// Markiere aktuellen Radiobutton beim Laden der Seite
function setRadioByData(data) {
    // Hole das Element mit der passenden ID
    console.log("setRadioByData: data = ", data.toLowerCase())
    const radio = document.getElementById('modus_' + data.toLowerCase() + '_button');

    // Überprüfe, ob das Element gefunden wurde
    if (radio) {
        // Setze den Radiobutton als ausgewählt
        radio.checked = true;
        // Disable unmoegliche Kombinationen
        const dummy = getCheckedRadioButtonValue()

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
            setTimeout(function() {sende_kommando(cmd)}, 200);});
        document.getElementById('modus_pause_button').addEventListener('change', () => {
            const cmd = cmd_build_modus();
            sende_kommando('/kommando/cpb');
            // Wenn der Timeout zu kurz ist, wird das Kommando vom Server nicht verarbeitet
            setTimeout(function() {sende_kommando(cmd);}, 200)});
}

function initializeElemente() {
    // Lese die Werte aus Meta-Element in <head>
    startwerte = $('#startwerte').data()
    var aktuellerModus = startwerte.modus;
    setRadioByData(aktuellerModus);
    document.getElementById('tempo_wert').value = startwerte.tempo_wert;
    document.getElementById('tempo_kommastellen').value = startwerte.tempo_kommastellen;
    document.getElementById('tempo_wert_value').textContent = startwerte.tempo_wert;
    document.getElementById('tempo_kommastellen_value').textContent = startwerte.tempo_kommastellen;
    document.getElementById('neuer_tempo_wert').textContent = Number(startwerte.tempo_wert) +
                                                              Number(startwerte.tempo_kommastellen);
    document.getElementById('date_kalkulations_zeit_datum').value = ISOalsDatum(startwerte.kalkulations_zeit);
    document.getElementById('time_kalkulations_zeit_uhrzeit').value = ISOalsUhrzeit(startwerte.kalkulations_zeit);
    document.getElementById('date_start_zeit_datum').value = ISOalsDatum(startwerte.start_zeit);
    document.getElementById('time_start_zeit_uhrzeit').value = ISOalsUhrzeit(startwerte.start_zeit);
}

initializeElemente()
registerListener()
setInterval(fetchData, 1000);
