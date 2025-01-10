import { calculateTimedeltaISO, calculateTextcolorTimedelta} from "./modules/datumUndZeit.js";

function updateUhrzeit(uhrzeitElementId, timedeltaElementId) {
    fetch('/get_aktuelle_uhrzeit')
        .then(response => response.json())
        .then(data => {
            const uhrzeitElement = document.getElementById(uhrzeitElementId);
            const timedeltaElement = document.getElementById(timedeltaElementId);
            const timedelta = calculateTimedeltaISO(data);
            const timedeltaTextcolor = calculateTextcolorTimedelta(data);

            uhrzeitElement.textContent = data;
            timedeltaElement.textContent = timedelta;
            timedeltaElement.style.color = timedeltaTextcolor;
        })
        .catch(error => {
            console.error('Fehler beim Abrufen der Uhrzeit:', error);
        });
}

// Aufruf der Funktion mit den richtigen Element-IDs
const uhrzeitElement = document.getElementById('aktuelle_uhrzeit');
const timedeltaElement = document.getElementById('timedelta');
setInterval(() => updateUhrzeit(uhrzeitElement.id, timedeltaElement.id), 1000);
