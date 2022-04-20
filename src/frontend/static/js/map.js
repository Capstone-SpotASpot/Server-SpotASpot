"use strict";
import { async_get_request, async_post_request } from './utils.js';

$(document).ready(async function() {
    // update it every 2 sec
    window.setInterval(async () => {
        const coords = await get_gps_coords();
        update_markers(coords.lat, coords.long, 10000)

    }, 6000) 
});


const icons = {
    taken: {
        icon: "/static/images/parking_spot_taken.png"
    },
    free: {
        icon: "/static/images/parking_spot_free.png"
    }
};

let markers = [];

export const initMap = async () => {
    const coords = await get_gps_coords();
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

    await update_markers(lat, long, 10000, map);
    map.set('styles', custom_style);

}

/**
 * @brief Updates the markers on the map for all of the parking spots around the coords given and radius
 */
const update_markers = async (lat, long, radius, map) =>
{
    // NOTE: radius is large, but on day of pres can make it small around Ell Hall
    const get_reader_url = `/mobile/get_local_readers?radius=${radius}&latitude=${lat}&longitude=${long}`;
    const readers = await async_get_request(get_reader_url, {});

    let parking_spots = {};

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
                spot_id: spot_id
            }
            parking_spots[spot_id] = cur_marker;
        }
    }

    // actually generate the markers
    for(const spot of Object.values(parking_spots))
    {
        // find the marker for this spot and update when it exists, create otherwise
        const marker_idx = get_marker_idx_for_spot(spot.spot_id);

        if(marker_idx == -1)
        {
            const marker = new google.maps.Marker({
                position: spot.position,
                icon: icons[spot.type].icon,
                map: map,
                spot_id: spot.spot_id
            });
            markers.push(marker);
        }
        // just update markers based on if their spot id is correct
        else{
            markers[marker_idx].icon = icons[spot.type].icon;
            markers[marker_idx].setIcon(icons[spot.type].icon);
        }

    };

}


/**
 * @returns {{
 *    coords: {
 *        latitude: Number,
 *        longitude: Number,
 *    }
 * }}
 */
const get_gps_coord_http = async () => {
    const coords_ret = {
        "coords": {
            "latitude": null,
            "longitude": null
        }
    }

    let raw_coords = null
    try {
        raw_coords = await $.get("http://ip-api.com/json")
    } catch (err) {
        console.log(`Failed to query google for coords: ${err}`)
        return coords_ret
    }

    if (raw_coords) {
        coords_ret.coords.latitude = raw_coords.lat
        coords_ret.coords.longitude = raw_coords.lon
    } else {
        // const conv_url = `http://maps.googleapis.com/maps/api/geocode/json?address=${raw_coords.zip}`
        // try {
        //     const coord_convert = await $.get(conv_url)
        //     console.log(coord_convert)
        //     if(coord_convert) {
        //         coords_ret.coords.latitude = coord_convert.results[0].geometry.location.lat
        //         coords_ret.coords.longitude = coord_convert.results[0].geometry.location.lng
        //     }
        // }
        // catch (err) {
        //     console.log(`Failed to query/read google for coords: ${err}`)
        //     return coords_ret
        // }
    }

    return coords_ret
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
    const pos = await new Promise( async (resolve, reject) =>{
        if (location.protocol === "https:") {
            navigator.geolocation.getCurrentPosition(resolve, reject, options);
        } else {
            try {
                const http_coords = await get_gps_coord_http()
                resolve(http_coords)
            } catch (err) {
                reject(err)
            }

        }
    });

    return {
        lat: pos.coords.latitude,
        long: pos.coords.longitude,
    };
}


// Returns the idx in markers for the given spot. -1 on failure
function get_marker_idx_for_spot(spot_id)
{
    for(let idx = 0; idx < markers.length; idx++)
    {
        if(markers[idx].spot_id == spot_id)
        {
            return idx;
        }
    }
    return -1;
}

// required explicit export for google maps api
window.initMap = initMap
