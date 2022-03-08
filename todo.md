# TODO for this repo

## MISC TODO:
* have add_tag api return the tag's id
* add the template / code to login as a user

## Implementation TODO's
* **procedures / funnctions**
  - [x] add_user
  - [x] add_tag
  - [x] add_car
    - [x] update_tag_pos
  - [x] add_spot
    - [x] check if any existing reader is in range of this new spot
  - [x] add_reader
    - [x] add to reader_coverage association table based on new reader
    - [x] functions: are_coords_in_range() & calc_coord_dist()
    - [x] also add_adjacent_reader???? as procedure that gets called
  - [x] add_observation_event
  - [x] add_detection_event
* **Test calls/selects for procedures&functions** - could be aman?
  - [x] test adding user
  - [ ] test adding tag
  - [ ] test adding car
  - [ ] test adding spot
  - [x] test adding reader
  - [ ] test adding adjacent readers
  - [ ] test adding detection event
  - [ ] test adding reader covering spot
* `reader_db_manager.py` -> make API function to save data from reader to database
* `mobile_app_db_manager.py` -> actually get status of spot from db
* `mobile_app_db_manager.py` -> actually get ID's of readers within gps radius
