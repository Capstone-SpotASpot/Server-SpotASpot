# TODO for this repo

## Setup todo's

* Actually set the `requirements.txt` right

## Implementation TODO's
* **procedures / funnctions**
  - [x] add_user
  - [x] add_tag
  - [x] add_car
    - [x] update_tag_pos
  - [x] add_spot
  - [x] add_reader
    - [ ] also add_adjacent_reader???? as function that gets called
      - for now keep it stand alone though
  - [x] add_observation_event
  - [x] add_detection_event
  - [ ] add_reader_coverage - **function**
    - would get called by add_reader or add_spot??
    - or by application?
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
