function fetchUhrzeit() {
    fetch('/get_aktuelle_uhrzeit')
    .then(response => response.json())
    .then(data => {
        const uhrzeitElement = document.getElementById('aktuelle_uhrzeit');
        uhrzeitElement.textContent = data;
    })
    .catch(error => {
        console.error('Fehler beim Abrufen der Uhrzeit:', error);
    });
}

// Daten alle 1 Sekunde abrufen
setInterval(fetchUhrzeit, 1000);
