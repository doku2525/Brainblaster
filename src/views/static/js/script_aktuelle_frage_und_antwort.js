// Lese den initialen Zustand aus dem Metaelement
const startwerte = $('#startwerte').data()

function vergleiche_frage(){
    // JavaScript (z.B. in einem setInterval)
    fetch('/get_aktuelle_frage_und_antwort')
        .then(response => response.json())
        .then(data => {
            // Vergleiche den neuen Zustand mit dem aktuellen Zustand
            console.log('startwerte frage = ', startwerte.frage)
            console.log('data frage= ', data.frage)
            if (startwerte.frage !== data.frage) {
                // Rufe die Route auf
                window.location.href = '/lade_neuen_zustand';
            }
        });
}

// Starte den Intervall, z.B. alle 2 Sekunden
setInterval(vergleiche_frage, 200);