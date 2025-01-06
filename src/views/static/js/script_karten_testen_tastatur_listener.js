document.addEventListener('keydown', (event) => {
    console.log('keydown event', event);
    if (event.key === '.') {
        window.location.href = '/karten_testen?zurueck=1';
    }
    if ('123456'.includes(event.key)) {
        window.location.href = `/kommando/ca${event.key}`;
    }
});

