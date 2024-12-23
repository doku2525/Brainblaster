export function ISOalsDatum(datetimeString) {
    const dateRegex = /^\d{4}-\d{2}-\d{2}/;
    return datetimeString.match(dateRegex)[0];
}

export function ISOalsUhrzeit(datetimeString) {
    const timeRegex = /\d{2}:\d{2}:\d{2}/;
    return datetimeString.match(timeRegex)[0];
}
