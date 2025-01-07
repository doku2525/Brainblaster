document.addEventListener('keydown', (event) => {
    console.log('keydown event', event);
    if (event.key === '.') {
        window.location.href = '/zeige_vokabelliste?zurueck=1';
    }
});

