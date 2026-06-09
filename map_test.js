// static/map.js

let map;

function initMap() {
    map = L.map('map').setView([20, 0], 2);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
}

function geocodeLocation(location, callback) {
    fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${location}`)
        .then(response => response.json())
        .then(data => {
            if (data && data.length > 0) {
                const lat = parseFloat(data[0].lat);
                const lon = parseFloat(data[0].lon);
                callback([lat, lon]);
            }
        })
        .catch(err => console.error("Geocoding error:", err));
}

function setMap(location) {
    initMap();
    geocodeLocation(location, coords => {
        L.marker(coords).addTo(map).bindPopup(location).openPopup();
        map.setView(coords, 6);

        // Force redraw to fix tile sizing
        setTimeout(() => {
            map.invalidateSize();
        }, 300);
    });
}

function setMultipleMarkers(locations) {
    initMap();
    locations.forEach(loc => {
        geocodeLocation(loc, coords => {
            L.marker(coords).addTo(map).bindPopup(loc);
        });
        setTimeout(() => {
            map.invalidateSize();
        }, 300);
    });
}
