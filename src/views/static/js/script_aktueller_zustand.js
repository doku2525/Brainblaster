// Lese den initialen Zustand aus dem Metaelement
const startwerte = $('#startwerte').data()
console.log('startwert zustand = ', startwerte.zustand)

function vergleiche_zustaende(){
    // JavaScript (z.B. in einem setInterval)
    fetch('/get_aktuellen_zustand')
        .then(response => response.json())
        .then(data => {
            // Vergleiche den neuen Zustand mit dem aktuellen Zustand
            if (startwerte.zustand !== data) {
                // Rufe die Route auf
                window.location.href = '/lade_neuen_zustand';
            }
        });
}

// Starte den Intervall, z.B. alle 2 Sekunden
setInterval(vergleiche_zustaende, 500);