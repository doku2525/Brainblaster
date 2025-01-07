document.addEventListener('keydown', (event) => {
    console.log('keydown event', event);
    if (event.key === '1') {
        window.location.href = '/kommando/c=0';
    }
    if (event.key === '2') {
        window.location.href = '/kommando/c=25';
    }
    if (event.key === '3') {
        window.location.href = '/kommando/c=81';
    }
    if (event.key === '4') {
        window.location.href = '/kommando/c=82';
    }
    if (event.key === '5') {
        window.location.href = '/kommando/c=80';
    }
    if (event.key === '+') {
        window.location.href = '/kommando/c+1';
    }
    if (event.key === '-') {
        window.location.href = '/kommando/c-1';Enter
    }
    if (event.key === 'Enter') {
        window.location.href = '/boxinfo';
    }
    if (event.key === '9') {
        window.location.href = '/kommando/cs';
    }
});

