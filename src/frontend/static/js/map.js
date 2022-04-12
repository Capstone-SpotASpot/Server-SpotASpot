"use strict";
import { async_get_request } from './utils.js';

$(document).ready(async function() {

    // initMap();
});


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

  const iconBase =
    "https://developers.google.com/maps/documentation/javascript/examples/full/images/";

    const icons = {
        parking: {
            icon: iconBase + "parking_lot_maps.png",
        },
    };

    // NOTE: radius is large, but on day of pres can make it small around Ell Hall
    const get_reader_url = `/mobile/get_local_readers?radius=${10000}&latitude=${lat}&longitude=${long}`;
    const readers = await async_get_request(get_reader_url, {});

    // add marker for each parking spot
    const features = readers.map( (lat_long_json) => {
        return {
            position: new google.maps.LatLng(lat_long_json.latitude, lat_long_json.longitude),
            type: "parking"
        };
    });

    // actually generate the markers
    for(const feat of features)
    {
        const marker = new google.maps.Marker({
            position: feat.position,
            icon: icons[feat.type].icon,
            map: map,
        })
    };

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
