// Owner Location Coordinate Picker with Leaflet

function initLocationPicker(mapId, latInputId, lngInputId, initialLat = 12.9716, initialLng = 77.5946) {
    const mapEl = document.getElementById(mapId);
    const latInput = document.getElementById(latInputId);
    const lngInput = document.getElementById(lngInputId);

    if (!mapEl || !latInput || !lngInput || typeof L === 'undefined') return;

    const startLat = parseFloat(latInput.value) || initialLat;
    const startLng = parseFloat(lngInput.value) || initialLng;

    const map = L.map(mapId).setView([startLat, startLng], 13);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);

    const marker = L.marker([startLat, startLng], {
        draggable: true
    }).addTo(map);

    function updateCoords(lat, lng) {
        latInput.value = lat.toFixed(8);
        lngInput.value = lng.toFixed(8);
    }

    // Set initial values if empty
    if (!latInput.value) updateCoords(startLat, startLng);

    marker.on('dragend', function (e) {
        const coord = e.target.getLatLng();
        updateCoords(coord.lat, coord.lng);
    });

    map.on('click', function (e) {
        marker.setLatLng(e.latlng);
        updateCoords(e.latlng.lat, e.latlng.lng);
    });
}
