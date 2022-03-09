# Server-SpotASpot APIs

## Reader APIs

To see what some of the data will look like, try running the tests found in
[test_reader_api](../src/backend/test/test_reader_api.sh) using the command `bash src/backend/test/test_reader_api.sh -r`.

### send_event_data

`http://71.167.9.86:31025/reader/send_event_data?reader_id=<reader_id>&tag_id=<tag_id>`

OR... if signal_strength is included (note, right now this does not affect anything at all)

`http://71.167.9.86:31025/reader/send_event_data?reader_id=<reader_id>&tag_id=<tag_id>&signal_strength=<signal_strength>`


- Probably the most important route for readers. Use this route to send observation data to the server
- `reader_id`: (int) The id of the reader sending the data
- `tag_id`: (int) The seen rfid tag's id
- `signal_strength`: (Optional, float) The strength of the rfid signal received
- `returns`: {"car_id": `car_id`,"detection_id": `detection_id`,"is_car_parked": `boolean`,"parked_spot_id": `parked_spot_id`}
  - Note: any returns of -1 denote errors or not enough info to make conclusive car detection
  - `car_id`: (int) The id of the car detected
  - `is_car_parked`: (bool) True if server determined a car is parked in the spot by the reader
  - `parking_spot_id`: (int) The id of the parking spot the car is parked in (-1 if not enough info)
  - `detection_id` (int) The id of the detection row stored in the database (-1 if not enough info)

To see the results for yourself, try running the tests found in
[test_detection_algo](../src/backend/test/test_detection_algo.sh) using the command `bash src/backend/test/test_detection_algo.sh -r`.


### add_reader

`http://71.167.9.86:31025/reader/add_reader?lat=<lat>&long=<long>&range=<range>&bearing=<bearing>`
- Use this route to add a reader
- `lat` & `long`: (float) Coordinates = (lat, long)
  - can look this up on google maps and click on a point to get the lat,long
- `range`: (float) Reader range (in meters)
- `bearing`: (float) Bearing angle to face the parking spot relattive to true north
  - Note, can get this by using most compasses (even iPhones come with a compass app)
- `returns`: {"new_reader_added": `<id of new reader>`}

## Mobile App APIs

To see what some of the data will look like, try running the tests found in
[test_mobile_api](../src/backend/test/test_mobile_api.sh) using the command `bash src/backend/test/test_mobile_api.sh -r`.


### get_local_readers

`http://71.167.9.86:31025/mobile/get_local_readers?radius=<radius>&latitude=<latitude>&longitude=<longitude>`
- Returns a list with every readers's id & coordinates in an area
- `latitude` & `longitude`: (float) Coordinates = (lat, long)
  - can look this up on google maps and click on a point to get the lat,long
- `radius`: (float) Area of valid readers - in meters - around the central point to return
- `returns`: [{"latitude":42.340988, "longitude":-71.091057, "reader_id": 1}, ...]

### get_is_spot_taken

`http://71.167.9.86:31025/mobile/get_is_spot_taken/<int:reader_id>`
- Tells querrier if the spot associated with the passed reader_id is taken
  - should be used in conjunction with `get_local_readers` to check all readers in a certain radius to fit on screen
- `reader_id`: The reader's spot to check if taken
- `returns`: Given a reader_id, returns the status of the spots it can reach.
  - {spot_id: {
      is_spot_taken: `<is_spot_taken>`,
      latitude: `<latitude>`,
      longitude: `<longitude>`,
      parked_car: `<parked_car>`}
    }
  - `is_spot_taken`: is a boolean
    - `True`: spot taken
    - `False`: spot not taken
    - `None`: some other state (i.e. an unregistered car is parked there)
  - `<latitude>` & `<longitude>` are the float values
  - `<parked_car>` Is the id (according to the database) of the car that is parked there
    - `null` if nothing is parked there

### get_spot_coord

`http://71.167.9.86:31025/mobile/get_spot_coord/<int:spot_id>`
- Gets the coordiantes of a spot/reader based on it's id
- `spot_id`: (int) id of the reader who's spot you want to get the coordinates for
- `returns`: {"latitude": `float`,"longitude": `float`}

## Car/Tag/User APIs

### Adding a New User / Signup

`http://71.167.9.86:31025/user/signup?fname=<fname>&lname=<lname>&username=<username>&pwd=<pwd>`

- `fname:`: The first name of the user
- `lname:`: The last name of the user
- `username:`: The user's username
- `pwd:`: Their password (will be hashed)
- `returns`: redirects to login page or back to registration if failed (basically nothing)


### User Forgot Password

`http://71.167.9.86:31025/user/forgot_password?uname=<uname>&new_pwd=<new_pwd>`
- `uname`: (str) The username whose password you are trying to change
- `new_pwd`: (str) The new password

### User Login

`http://71.167.9.86:31025/user/login?username=<username>&pwd=<pwd>`
- `uname`: (str) The username to login with
- `pwd`: (str) The password associated with the username to login with

### Get User Id

`http://71.167.9.86:31025/user/get_id`
- `returns`: {'user_id': `<id>`}
- **Note:** You have to be logged in to get this
### Adding a New Car

`http://71.167.9.86:31025/cars/add_car?front_tag=<front_tag>&middle_tag=<middle_tag>&rear_tag=<rear_tag>`
- Used to add a new car to the database
- **Note:** Have to be logged in to add a car
- `front_tag`, `middle_tag`, `rear_tag` the id's of the 3 tags on the car (according to the database)
- `returns`: {"new_car_id": `int`}
  - The id of the new car

### Adding a New Tag

`http://71.167.9.86:31025/cars/add_tag`
- adds a tag to the database (not associated with any car yet)
- `returns`: {"new_tag_id": `int`}
  - the id of the new tag

