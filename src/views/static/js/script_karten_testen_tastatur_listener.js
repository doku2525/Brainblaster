document.addEventListener('keydown', (event) => {
    console.log('keydown event', event);
    if (event.key === '.') {
        window.location.href = '/karten_testen?zurueck=1';
    }
    if ('123456'.includes(event.key)) {
        // Wenn sich keine Karte mehr in der Liste befindet, keine Kommandos mehr abschicken, sondern zurueck.
        if ($('#startwerte').data().frage === 'Fertig')  {
            window.location.href = '/karten_testen?zurueck=1';
        } else {
            window.location.href = `/kommando/ca${event.key}`;
        }
    }
});

