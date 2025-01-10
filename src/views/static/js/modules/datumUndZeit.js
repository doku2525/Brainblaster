export function ISOalsDatum(datetimeString) {
    const dateRegex = /^\d{4}-\d{2}-\d{2}/;
    return datetimeString.match(dateRegex)[0];
}

export function ISOalsUhrzeit(datetimeString) {
    const timeRegex = /\d{2}:\d{2}:\d{2}/;
    return datetimeString.match(timeRegex)[0];
}

export function calculateTimedeltaISO(datetimeString) {
    const nullTimedelta = '0T 00:00:00';
    const nullDelta = 1600;
    if (datetimeString === '0') {return nullTimedelta}
    const lernuhr = new Date(datetimeString);
    const now = new Date();
    const differenceInMilliseconds = now.getTime() - lernuhr.getTime();

    // Um den moegliche Verzoegerungen (im Testlauf etwa 1sek) zwischen Servers echte_zeit() und hier auszugleichen,
    // werden Werte kleiner als 1,6 sek als 0 sek Zeitunterschied gewertet.
    if (Math.abs(differenceInMilliseconds) < nullDelta) {return nullTimedelta}

    // Bei negativen Werten wird sofort -1T angezeigt, deshalb erst mit positiven Werten rechnen um -0T zu erhalten
    const sekunden = Math.floor(Math.abs(differenceInMilliseconds) / 1000);
    const minuten = Math.floor(sekunden / 60);
    const stunden = Math.floor(minuten / 60);
    const tage = Math.floor(stunden / 24);

    // Formatierung mit führenden Nullen
    const formatierteStunde = Math.abs(stunden % 24).toString().padStart(2, '0');
    const formatierteMinuten = Math.abs(minuten % 60).toString().padStart(2, '0');
    const formatierteSekunden = Math.abs(sekunden % 60).toString().padStart(2, '0');
    const result = `${tage}T ${formatierteStunde}:${formatierteMinuten}:${formatierteSekunden}`;
    if (differenceInMilliseconds > -nullDelta) { return result}
    return `-${result}`
}

export function calculateTextcolorTimedelta(datetimeString) {
    const nullDelta = 1600;
    if (datetimeString === '0') {return 'black'}
    const lernuhr = new Date(datetimeString);
    const now = new Date();
    const differenceInMilliseconds = now.getTime() - lernuhr.getTime();
    if (differenceInMilliseconds > nullDelta) { return 'blue' };
    if (differenceInMilliseconds < -nullDelta) { return 'red' };
    return 'black'
}
