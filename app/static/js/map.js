// Leaflet OpenStreetMap Controller for PG & Room Finder

function initSearchMap(mapElementId, properties) {
    const mapEl = document.getElementById(mapElementId);
    if (!mapEl || typeof L === 'undefined') return null;

    // Default center (Bangalore) if list is empty
    let defaultLat = 12.9716;
    let defaultLng = 77.5946;

    if (properties && properties.length > 0 && properties[0].latitude) {
        defaultLat = parseFloat(properties[0].latitude);
        defaultLng = parseFloat(properties[0].longitude);
    }

    const map = L.map(mapElementId, {
        zoomControl: true,
        scrollWheelZoom: false
    }).setView([defaultLat, defaultLng], 12);

    // OpenStreetMap CartoDB Dark Matter / Standard tiles
    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 19
    }).addTo(map);

    const markers = [];

    // Custom marker icon
    const customIcon = L.divIcon({
        className: 'custom-leaflet-marker',
        html: `<div style="
            background: linear-gradient(135deg, #6366f1 0%, #4338ca 100%);
            color: #ffffff;
            font-weight: 700;
            font-size: 11px;
            padding: 5px 9px;
            border-radius: 20px;
            border: 2px solid #ffffff;
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
            white-space: nowrap;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 4px;
        "><i class="fas fa-home"></i> PG</div>`,
        iconSize: [60, 30],
        iconAnchor: [30, 15]
    });

    if (properties && Array.isArray(properties)) {
        properties.forEach(p => {
            if (!p.latitude || !p.longitude) return;

            const lat = parseFloat(p.latitude);
            const lng = parseFloat(p.longitude);

            const popupContent = `
                <div class="map-popup-card">
                    <img src="${p.cover_image || 'https://images.unsplash.com/photo-1555854877-bab0e564b8d5?auto=format&fit=crop&w=800&q=80'}" class="map-popup-img" alt="${p.title}">
                    <div class="map-popup-body">
                        <h4 class="map-popup-title">${p.title}</h4>
                        <div class="map-popup-price">₹${parseInt(p.min_price).toLocaleString()} <span>/mo</span></div>
                        <a href="/property/${p.slug}" class="map-popup-btn">View Details</a>
                    </div>
                </div>
            `;

            const marker = L.marker([lat, lng], { icon: customIcon })
                .addTo(map)
                .bindPopup(popupContent);

            markers.push(marker);
        });

        if (markers.length > 0) {
            const group = new L.featureGroup(markers);
            map.fitBounds(group.getBounds().pad(0.15));
        }
    }

    return map;
}

function initDetailMap(mapElementId, lat, lng, title) {
    const mapEl = document.getElementById(mapElementId);
    if (!mapEl || typeof L === 'undefined') return null;

    const map = L.map(mapElementId, {
        scrollWheelZoom: false
    }).setView([lat, lng], 15);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        subdomains: 'abcd',
        maxZoom: 19
    }).addTo(map);

    const marker = L.marker([lat, lng]).addTo(map);
    marker.bindPopup(`<b>${title}</b><br>Accurate Location`).openPopup();

    return map;
}
