-- SpotASpot Database Creation Code

DROP DATABASE IF EXISTS SpotASpot_dev;

CREATE DATABASE IF NOT EXISTS SpotASpot_dev;

USE SpotASpot_dev;

DROP TABLE IF EXISTS readers;

CREATE TABLE readers
(
    reader_id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    latitude FLOAT( 10, 6 ) NOT NULL,
    longitude FLOAT( 10, 6 ) NOT NULL,
    reader_range FLOAT NOT NULL -- range in meters
);

-- Create recursive reader relationship
DROP TABLE IF EXISTS adjacent_readers;
CREATE TABLE adjacent_readers
(
    adjacency_id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,

    -- Pairs 2 readers together if they are in range of each other.
    -- The order does NOT matter
    reader_one INT NOT NULL,
    reader_two INT NOT NULL,

    -- the readers are FK to the actual reader table
    CONSTRAINT FK_reader_one
        FOREIGN KEY (reader_one) REFERENCES readers(reader_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT FK_reader_two
        FOREIGN KEY (reader_two) REFERENCES readers(reader_id)
        ON UPDATE CASCADE ON DELETE CASCADE

);

DROP TABLE IF EXISTS users;
CREATE TABLE users
(
    user_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    user_password VARCHAR(50) NOT NULL
);

-- Need the tag table so it can be a FK in the car table
DROP TABLE IF EXISTS tag;
CREATE TABLE tag
(
    -- the id will get set by how the tag is programmed
    tag_id INT PRIMARY KEY NOT NULL,
    car_pos ENUM('front', 'rear', 'middle')
);

DROP TABLE IF EXISTS registered_cars;
CREATE TABLE registered_cars
(
    car_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    front_tag INT NOT NULL,
    middle_tag INT NOT NULL,
    rear_tag INT NOT NULL,
    registering_user INT NOT NULL,

    -- tags are FK to the tag table
    CONSTRAINT front_tag_fk
        FOREIGN KEY (front_tag)
        REFERENCES tag(tag_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT middle_tag_fk
        FOREIGN KEY (middle_tag)
        REFERENCES tag(tag_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT rear_tag_fk
        FOREIGN KEY (rear_tag)
        REFERENCES tag(tag_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT registering_user_fk
        FOREIGN KEY (registering_user)
        REFERENCES users(user_id)
        ON UPDATE RESTRICT ON DELETE CASCADE
);


DROP TABLE IF EXISTS parking_spot;
CREATE TABLE parking_spot
(
    spot_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    longitude FLOAT( 10, 6 ) NOT NULL,
    latitude FLOAT( 10, 6 ) NOT NULL,

    -- allowed to be null when no car is parked
    time_since_parked TIMESTAMP,
    parked_car_id INT NULL,

    CONSTRAINT parked_car_fk
        FOREIGN KEY (parked_car_id)
        REFERENCES registered_cars (car_id)
        ON UPDATE CASCADE ON DELETE SET NULL
);

DROP TABLE IF EXISTS observation_event;
CREATE TABLE observation_event
(
    observation_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    time_observed DATETIME NOT NULL,
    signal_strength FLOAT NOT NULL,

    -- Used to keep track of old events that no longer factor into algo's
    is_relevant boolean NOT NULL
);

-- Association Tables

-- association between parking_spot and reader tables
DROP TABLE IF EXISTS reader_coverage;
CREATE TABLE reader_coverage
(
    coverage_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    covering_reader_id INT NOT NULL,
    spot_covered_id INT NOT NULL,

    -- create FK for association table relationships
    CONSTRAINT reader_cover_fk
        FOREIGN KEY (covering_reader_id)
        REFERENCES readers(reader_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT covered_spot_fk
        FOREIGN KEY (spot_covered_id)
        REFERENCES parking_spot(spot_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-- associate reader-tag-observation_event
DROP TABLE IF EXISTS detects;
CREATE TABLE detects
(
    detection_id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    detecting_reader_id INT NOT NULL,
    detected_tag_id INT NOT NULL,
    observation_event_id INT NOT NULL,

    CONSTRAINT detects_reader_fk
        FOREIGN KEY (detecting_reader_id)
        REFERENCES readers (reader_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT detects_tag_fk
        FOREIGN KEY (detected_tag_id)
        REFERENCES tag (tag_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT detects_event_fk
        FOREIGN KEY (observation_event_id)
        REFERENCES observation_event (observation_id)
        ON UPDATE CASCADE ON DELETE CASCADE
);


-- ###### Start of Functions ######



DROP FUNCTION IF EXISTS calc_coord_dist;
DELIMITER $$
-- checks if two pts in 3D space are in range of each other
-- given: latitude & longitude of both points & radius
-- returns: true/false
-- REF: https://stackoverflow.com/a/501224
-- REF2: https://dev.mysql.com/blog-archive/spatial-reference-systems-in-mysql-8-0/
CREATE FUNCTION calc_coord_dist (
  long1 FLOAT (10,6),
  lat1 FLOAT (10,6),
  long2 FLOAT (10,6),
  lat2 FLOAT (10,6)
)
  RETURNS FLOAT
  DETERMINISTIC
BEGIN
  RETURN(ST_Distance(
    ST_SRID(Point(lat1, long1), 4326),
    ST_SRID(Point(lat2, long2), 4326)
  ));
END $$
-- end of calc_coord_dist
-- resets the DELIMETER
DELIMITER ;


DROP FUNCTION IF EXISTS are_coords_in_range;
DELIMITER $$
-- checks if two pts in 3D space are in range of each other
-- given: latitude & longitude of both points & radius
-- returns: true/false
CREATE FUNCTION are_coords_in_range(
  long1 FLOAT (10,6),
  lat1 FLOAT (10,6),
  long2 FLOAT (10,6),
  lat2 FLOAT (10,6),
  radius FLOAT
)
  RETURNS BOOLEAN
  DETERMINISTIC
BEGIN
  DECLARE coord_dist FLOAT;
  DECLARE is_in_range BOOLEAN;
  SET coord_dist = (SELECT calc_coord_dist(long1, lat1, long2, lat2));
  SET is_in_range = (SELECT coord_dist <= radius);
  RETURN(is_in_range);
END $$
-- end of are_coords_in_range
-- resets the DELIMETER
DELIMITER ;

-- ###### End of Functions ######



-- ###### Start of Procedures ######

DROP PROCEDURE IF EXISTS add_user;
DELIMITER $$
-- adds a user to the database and returns their id
CREATE PROCEDURE add_user(
  IN fname VARCHAR(50),
  IN lname VARCHAR(50),
  IN username VARCHAR(50),
  IN pwd VARCHAR(50)
) BEGIN

  DECLARE created_user_id INT;
  -- In case adding a user fails
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    SHOW ERRORS;
    ROLLBACK;
  END;

  START TRANSACTION;

  -- note: the username col is set to unique so duplicates wont happen
  INSERT INTO users(user_id, first_name, last_name, username, user_password)
    VALUES (DEFAULT, fname, lname, username, MD5(pwd));
  SET created_user_id = LAST_INSERT_ID();
  SELECT created_user_id as 'created_user_id';

  COMMIT;

END $$
-- end of add_user
-- resets the DELIMETER
DELIMITER ;

DROP PROCEDURE IF EXISTS add_reader;
DELIMITER $$

CREATE PROCEDURE add_reader(
  IN p_reader_lat FLOAT( 10, 6 ),
  IN p_reader_long FLOAT( 10, 6 ),
  IN p_reader_range FLOAT
) BEGIN
  DECLARE created_reader_id INT;
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    SHOW ERRORS;
    ROLLBACK;
  END;
  START TRANSACTION;

  -- create the reader row
  INSERT INTO readers (reader_id, latitude, longitude, reader_range)
    VALUES (DEFAULT, p_reader_lat, p_reader_long, p_reader_range);
  SET created_reader_id = LAST_INSERT_ID();

  -- determine which spots are in range of the reader
  -- TODO: check for antenna/reader direction??
  INSERT INTO reader_coverage (covering_reader_id, spot_covered_id)
  SELECT created_reader_id, parking_spot.spot_id
  FROM parking_spot
  WHERE (
    SELECT are_coords_in_range(
      p_reader_lat,
      p_reader_long,
      parking_spot.latitude,
      parking_spot.longitude,
      p_reader_range
    )
  );

  COMMIT;
END $$
-- end of add_reader
-- resets the DELIMETER
DELIMITER ;

DROP PROCEDURE IF EXISTS add_tag;
DELIMITER $$
-- creates a new tag and adds to the database
-- returns the new tag's ID for user client side
CREATE PROCEDURE add_tag() BEGIN
  -- use transaction bc multiple inserts and should rollback on error
  DECLARE new_tag_id INT;
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    SHOW ERRORS;
    ROLLBACK;
  END;
  START TRANSACTION; -- may need to rollback bc multiple inserts

  -- leave car position blank as it will be filled in later
  INSERT INTO tag (tag_id) VALUES (DEFAULT);
  SET new_tag_id = LAST_INSERT_ID(); -- get id of last inserted row into a table
  SELECT new_tag_id as 'new_tag_id';

  COMMIT;
END $$
-- end of add_tag
-- resets the DELIMETER
DELIMITER ;

DROP PROCEDURE IF EXISTS add_car;
DELIMITER $$
-- adds a car element to the database
-- & updates the tag table to include position on a car
-- returns the id of the new car
CREATE PROCEDURE add_car(
  IN user_id_in INT,
  IN tag_id_front INT,
  IN tag_id_middle INT,
  IN tag_id_rear INT
) BEGIN
  -- use transaction bc multiple inserts and should rollback on error
  DECLARE created_car_id INT;
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    SHOW ERRORS;
    ROLLBACK;
  END;
  START TRANSACTION; -- may need to rollback bc multiple inserts

  -- leave car position blank as it will be filled in later
  UPDATE tag SET car_pos = 'front' WHERE tag_id = tag_id_front;
  UPDATE tag SET car_pos = 'middle' WHERE tag_id = tag_id_middle;
  UPDATE tag SET car_pos = 'rear' WHERE tag_id = tag_id_rear;

  INSERT INTO registered_cars (car_id, registering_user, front_tag, middle_tag, rear_tag)
  VALUES (DEFAULT, user_id_in, tag_id_front, tag_id_middle, tag_id_rear);

  SET created_car_id = LAST_INSERT_ID(); -- get id of last inserted row into a table
  SELECT created_car_id as 'created_car_id';
  COMMIT;
END $$
-- end of add_car
-- resets the DELIMETER
DELIMITER ;

DROP PROCEDURE IF EXISTS add_spot;
DELIMITER $$
-- adds a parking spot to the database
-- given: coordinates (longitude & latitude)
-- returns: created spot's id
CREATE PROCEDURE add_spot(
  IN longitude_in float(10,6),
  IN latitude_in float(10,6)
) BEGIN  -- use transaction bc multiple inserts and should rollback on error
  DECLARE created_spot_id INT;
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    SHOW ERRORS;
    ROLLBACK;
  END;
  START TRANSACTION; -- may need to rollback bc multiple inserts

  INSERT INTO parking_spot (spot_id, longitude, latitude, parked_car_id, time_since_parked)
  VALUES (DEFAULT, longitude_in, latitude_in, NULL, NULL);

  SET created_spot_id = LAST_INSERT_ID();
  SELECT created_spot_id as 'created_spot_id';

  COMMIT;
END $$
-- end of add_spot
-- resets the DELIMETER
DELIMITER ;

DROP PROCEDURE IF EXISTS add_observation_event;
DELIMITER $$
-- adds a reader observation event to a table in database
-- given: observed time, signal strength
-- returns: created id
CREATE PROCEDURE add_observation_event(
  IN observation_time_in DATETIME,
  IN signal_strength_in FLOAT

) BEGIN  -- use transaction bc multiple inserts and should rollback on error
  DECLARE created_observ_id INT;
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    SHOW ERRORS;
    ROLLBACK;
  END;
  START TRANSACTION; -- may need to rollback bc multiple inserts

  INSERT INTO observation_event(observation_id, time_observed, signal_strength, is_relevant)
  VALUES (DEFAULT, observation_time_in, signal_strength_in, true);

  SET created_observ_id = LAST_INSERT_ID();
  SELECT created_observ_id as 'created_observ_id';

  COMMIT;
END $$
-- end of add_observation_event
-- resets the DELIMETER
DELIMITER ;


DROP PROCEDURE IF EXISTS add_detection_event;
DELIMITER $$
-- adds a detected car event to the association table in database
-- given: reader_id responsible for event, seen tag_id, observation_id
-- returns: created id
CREATE PROCEDURE add_detection_event(
  IN reader_id_in INT,
  IN seen_tag_id_in INT,
  IN observation_id_in INT

) BEGIN  -- use transaction bc multiple inserts and should rollback on error
  DECLARE created_detect_id INT;
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    SHOW ERRORS;
    ROLLBACK;
  END;
  START TRANSACTION; -- may need to rollback bc multiple inserts

  INSERT INTO detects (detection_id, detecting_reader_id, detected_tag_id, observation_event_id)
  VALUES (DEFAULT, reader_id_in, seen_tag_id_in, observation_id_in);

  SET created_detect_id = LAST_INSERT_ID();
  SELECT created_detect_id as 'created_detect_id';

  COMMIT;
END $$
-- end of add_detection_event
-- resets the DELIMETER
DELIMITER ;


-- ###### End of Procedures ######

INSERT INTO readers (longitude, latitude, reader_range)
    VALUES (0.0, 0.0, 20), (1.0, 1.0, 20)
