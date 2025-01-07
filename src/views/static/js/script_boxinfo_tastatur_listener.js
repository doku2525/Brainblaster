document.addEventListener('keydown', (event) => {
    console.log('keydown event', event);
    if (event.key === '.') {
        window.location.href = '/index?lernuhr=ohne_speichern';
    }
    if ('6'.includes(event.key)) {
        window.location.href = '/kommando/c+1';
    }
    if ('4'.includes(event.key)) {
        window.location.href = '/kommando/c-1';
    }
    if ('1'.includes(event.key)) {
        window.location.href = '/karten_pruefen';
    }
    if ('2'.includes(event.key)) {
        window.location.href = '/karten_lernen';
    }
    if ('3'.includes(event.key)) {
        window.location.href = '/karten_neue';
    }
    if ('7'.includes(event.key)) {
        window.location.href = '/zeige_vokabelliste_komplett';
    }
    if ('8'.includes(event.key)) {
        window.location.href = '/zeige_vokabelliste_lernen';
    }
    if ('9'.includes(event.key)) {
        window.location.href = '/zeige_vokabelliste_neue';
    }
});
