// Datei initializiert alphaWavesSound als globales Objekt, damit es auch bei einem Seitenwechsel weiter laeuft
// let alphaWavesSound;

function initAlphaWavesSound() {
    if (!window.alphaWavesSound) {
        window.alphaWavesSound = new Howl({
            src: ['../static/musik/alpha_waves.mp3'],
            loop: true
        });
        console.log("Neues Element alphaWaveSound initializiert!")
    } else {console.log("Kein neues Element alphaWaveSound initializiert!")}
}

window.onload = initAlphaWavesSound;