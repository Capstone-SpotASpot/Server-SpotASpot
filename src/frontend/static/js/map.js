"use strict";
import { async_get_request } from './utils.js';

$(document).ready(async function() {

    // initMap();
});


const icons = {
    taken: {
        icon: "/static/images/parking_spot_taken.png"
    },
    free: {
        icon: "/static/images/parking_spot_free.png"
    }
};

// key = spot id
const parking_spots = {};

export const initMap = async () => {
    const coords = await get_gps_coords();
    console.log(`my (lat, long): (${coords.lat}, ${coords.long})`)
    create_map(coords.lat, coords.long);
}

const create_map = async (lat, long) => {
    const map = new google.maps.Map(document.getElementById("map"), {
        center: new google.maps.LatLng(lat, long),
        zoom: 16,
        gestureHandling: "passive",
    });

    // https://developers.google.com/maps/documentation/javascript/style-reference
    const custom_style = [
        {
            featureType: "all",
            elementType: "labels",
            stylers: [
                { visibility: "off" }
            ],
        },
        {
            featureType: "poi.school",
            elementType: "labels",
            stylers: [
            { visibility: "on" }
            ],
        },
    ]

    map.set('styles', custom_style);

    // NOTE: radius is large, but on day of pres can make it small around Ell Hall
    const get_reader_url = `/mobile/get_local_readers?radius=${10000}&latitude=${lat}&longitude=${long}`;
    const readers = await async_get_request(get_reader_url, {});

    // const parking_spots = [];
    for (const reader of readers)
    {
        const get_spot_status_url = `/mobile/get_is_spot_taken/${reader.reader_id}`
        const spot_statuses = await async_get_request(get_spot_status_url, {});


        for(const [spot_id, spot] of Object.entries(spot_statuses))
        {
            // process each spot seen by a reader
            const type = spot.is_spot_taken ? "taken" : "free";
            const cur_marker = {
                position: new google.maps.LatLng(spot.latitude, spot.longitude),
                type: type,
            }
            // parking_spots.push(cur_marker);
            parking_spots[spot_id] = cur_marker;
        }
    }

    // actually generate the markers
    for(const spot of Object.values(parking_spots))
    {
        const marker = new google.maps.Marker({
            position: spot.position,
            icon: icons[spot.type].icon,
            map: map,
        })
    };

}

/**
 * @brief Given a JSON of parking spots statuses from the /mobile/get_is_spot_taken route,
 * updates the markers on the map
 * @param {Array} parking_spots The parking spots to check the status of
 */
const update_markers = async (parking_spots) =>
{
}

/**
 *
 * @returns {{
 *              long: Number,
 *              lat: Number
 * }}
 */
const get_gps_coords = async () =>
{
    const options = {
        enableHighAccuracy: true,
        timeout: 5000,
        maximumAge: 0
    };

    // Try to await the request
    const pos = await new Promise((resolve, reject) =>{
        navigator.geolocation.getCurrentPosition(resolve, reject, options);
    });

    return {
        long: pos.coords.longitude,
        lat: pos.coords.latitude,
    };
}

// required explicit export for google maps api
window.initMap = initMap
