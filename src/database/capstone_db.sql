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
    tag_id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
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
        ON UPDATE CASCADE ON DELETE CASCADE
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
    tag_seen_id INT NOT NULL,

    -- Used to keep track of old events that no longer factor into algo's
    is_relevant boolean NOT NULL,

    CONSTRAINT observation_tag_fk
        FOREIGN KEY (tag_seen_id)
        REFERENCES tag (tag_id)
        ON UPDATE CASCADE ON DELETE CASCADE
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
    -- it takes 3 tags to make the observation - a full car
    observation_event1_id INT NOT NULL,
    observation_event2_id INT NOT NULL,
    observation_event3_id INT NOT NULL,

    CONSTRAINT detects_reader_fk
        FOREIGN KEY (detecting_reader_id)
        REFERENCES readers (reader_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT observation1_fk
        FOREIGN KEY (observation_event1_id)
        REFERENCES observation_event (observation_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT observation2_fk
        FOREIGN KEY (observation_event2_id)
        REFERENCES observation_event (observation_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT observation3_fk
        FOREIGN KEY (observation_event3_id)
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
-- adds a user to the database and returns their id (-1 if error)
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
    SELECT -1 as 'created_user_id';
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

-- creates a reader and returns the id of the newly added row
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

  SELECT created_reader_id as 'created_reader_id';

  COMMIT;
END $$
-- end of add_reader
-- resets the DELIMETER
DELIMITER ;

DROP PROCEDURE IF EXISTS add_tag;
DELIMITER $$
-- creates a new tag and adds to the database
-- returns the new tag's ID for user client side (-1 for error)
CREATE PROCEDURE add_tag() BEGIN
  -- use transaction bc multiple inserts and should rollback on error
  DECLARE new_tag_id INT;
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    SHOW ERRORS;
    ROLLBACK;
    SELECT -1 AS 'new_tag_id';
  END;
  START TRANSACTION; -- may need to rollback bc multiple inserts

  -- leave car position blank as it will be filled in later
  INSERT INTO tag (tag_id) VALUES (DEFAULT);
  SET new_tag_id = LAST_INSERT_ID(); -- get id of last inserted row into a table
  SELECT new_tag_id AS 'new_tag_id';

  COMMIT;
END $$
-- end of add_tag
-- resets the DELIMETER
DELIMITER ;

DROP PROCEDURE IF EXISTS add_car;
DELIMITER $$
-- adds a car element to the database
-- & updates the tag table to include position on a car
-- returns the id of the new car (-1 for error)
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
    SELECT -1 as 'created_car_id';
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
  IN spot_long_in float(10,6),
  IN spot_lat_in float(10,6)
) BEGIN  -- use transaction bc multiple inserts and should rollback on error
  DECLARE created_spot_id INT;
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    SHOW ERRORS;
    ROLLBACK;
  END;
  START TRANSACTION; -- may need to rollback bc multiple inserts

  INSERT INTO parking_spot (spot_id, longitude, latitude, parked_car_id, time_since_parked)
  VALUES (DEFAULT, spot_long_in, spot_lat_in, NULL, NULL);
  SET created_spot_id = LAST_INSERT_ID();

  -- determine if new spot is in range of an existing reader
  -- TODO: check for antenna/reader direction??
  INSERT INTO reader_coverage (covering_reader_id, spot_covered_id)
  SELECT readers.reader_id, created_spot_id
  FROM readers
  WHERE (
    SELECT are_coords_in_range(
      readers.latitude,
      readers.longitude,
      spot_lat_in,
      spot_long_in,
      readers.reader_range
    )
  );

  SELECT created_spot_id as 'created_spot_id';

  COMMIT;
END $$
-- end of add_spot
-- resets the DELIMETER
DELIMITER ;

DROP PROCEDURE IF EXISTS add_observation;
DELIMITER $$
-- adds a reader observation event to observation and detection association table in database
-- given: observed time, signal strength, reader id, tag id
-- returns: created id
CREATE PROCEDURE add_observation(
  IN observation_time_in DATETIME,
  IN signal_strength_in FLOAT,
  IN reader_id_in INT,
  IN seen_tag_id_in INT
) BEGIN  -- use transaction bc multiple inserts and should rollback on error
  DECLARE created_observ_id INT;
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    SHOW ERRORS;
    ROLLBACK;
  END;
  START TRANSACTION; -- may need to rollback bc multiple inserts

  INSERT INTO observation_event(observation_id, time_observed, signal_strength, is_relevant, tag_seen_id)
  VALUES (DEFAULT, observation_time_in, signal_strength_in, true, seen_tag_id_in);

  SET created_observ_id = LAST_INSERT_ID();
  SELECT created_observ_id as 'created_observ_id';
  COMMIT;
END $$
-- end of add_observation
-- resets the DELIMETER
DELIMITER ;

DROP PROCEDURE IF EXISTS add_detection;
DELIMITER $$
-- adds 3 reader observation event
-- given: observed time, signal strength, reader id, tag id
-- returns: created id
CREATE PROCEDURE add_detection(
  IN reader_id_in INT,
  IN observation_event1_id_in INT,
  IN observation_event2_id_in INT,
  IN observation_event3_id_in INT
) BEGIN  -- use transaction bc multiple inserts and should rollback on error
  DECLARE created_detect_id INT;
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    SHOW ERRORS;
    ROLLBACK;
  END;
  START TRANSACTION; -- may need to rollback bc multiple inserts

  INSERT INTO detects (detection_id, detecting_reader_id,
                      observation_event1_id, observation_event2_id,
                      observation_event3_id)
  VALUES (DEFAULT, reader_id_in, observation_event1_id_in,
        observation_event2_id_in, observation_event3_id_in);

  SET created_detect_id = LAST_INSERT_ID();
  SELECT created_detect_id as 'created_detect_id';
  COMMIT;
END $$
-- end of add_detection
-- resets the DELIMETER
DELIMITER ;


DROP PROCEDURE IF EXISTS add_adjacent_reader;
DELIMITER $$
-- adds two readers as adjacent to one another in database
-- given: reader_ids for both
-- returns: created adjacency id
CREATE PROCEDURE add_adjacent_reader(
  IN reader1_in INT,
  IN reader2_in INT
) BEGIN  -- use transaction bc multiple inserts and should rollback on error
  DECLARE created_adj_id INT;
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    SHOW ERRORS;
    ROLLBACK;
  END;
  START TRANSACTION; -- may need to rollback bc multiple inserts

  INSERT INTO adjacent_readers (adjacency_id, reader_one, reader_two)
  VALUES (DEFAULT, reader1_in, reader2_in);

  SET created_adj_id = LAST_INSERT_ID();
  SELECT created_adj_id as 'created_adj_id';

  COMMIT;
END $$
-- resets the DELIMETER
DELIMITER ;


DROP PROCEDURE IF EXISTS is_spot_taken;
DELIMITER $$
-- given: reader_id
-- returns: status of all spots the given reader can cover ()
CREATE PROCEDURE is_spot_taken(
  IN reader_id_in INT
) BEGIN  -- use transaction bc multiple inserts and should rollback on error
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    SHOW ERRORS;
    ROLLBACK;
  END;
  START TRANSACTION; -- may need to rollback bc multiple inserts
    -- Get the spot's that the reader covers through coverage table
    SELECT  parking_spot.spot_id as spot_id,
            parking_spot.longitude as longitude,
            parking_spot.latitude as latitude,
        -- spot is free = 0, taken = 1
        CASE parked_car_id
            WHEN NULL THEN 0
            WHEN NOT NULL THEN 1
            ELSE -1
        END as spot_status
        FROM readers
        JOIN reader_coverage
            ON readers.reader_id = reader_coverage.covering_reader_id
        LEFT JOIN parking_spot
            ON reader_coverage.spot_covered_id = parking_spot.spot_id;

  COMMIT;
END $$
-- end of is_spot_taken
-- resets the DELIMETER
DELIMITER ;

-- ###### End of Procedures ######

-- ##### Add one set of rows #####
-- 1 spot, 2 reader, 1 adjacent readers, 1 user, 1 car, 3 tags, 3 observation event, 1 detects
-- reader coverage is handled by other insert procedures

-- add 1 spot
CALL add_spot(42.341885, -71.090590);

-- add 2 readers
CALL add_reader(42.341013, -71.091145, 40);
SET @reader_1_id = LAST_INSERT_ID();
CALL add_reader(42.342008, -71.090526, 50);
SET @reader_2_id = LAST_INSERT_ID();

-- add 1 adjacent readers
CALL add_adjacent_reader(@reader_1_id, @reader_2_id);

-- add 1 user
CALL add_user(
  "test_first_name", "test_last_name",
  "test_user", "test_pwd"
);

SET @user1_id = LAST_INSERT_ID();

-- add 3 tags
CALL add_tag();
SET @tag1_id = LAST_INSERT_ID();
CALL add_tag();
SET @tag2_id = LAST_INSERT_ID();
CALL add_tag();
SET @tag3_id = LAST_INSERT_ID();


-- add 1 car
CALL add_car(
  @user1_id, @tag1_id,
  @tag2_id, @tag3_id
);


-- add 3 observation event
CALL add_observation(
  "2022-02-06 10:20:30",
  13,
  @reader_1_id,
  @tag1_id
);

SET @observe1_id = LAST_INSERT_ID();

CALL add_observation(
  "2022-02-06 10:20:31",
  15,
  @reader_1_id,
  @tag1_id
);

SET @observe2_id = LAST_INSERT_ID();

CALL add_observation(
  "2022-02-06 10:20:31",
  14.5,
  @reader_1_id,
  @tag1_id
);

SET @observe3_id = LAST_INSERT_ID();

-- add 1 detects car (need 3 observations)
CALL add_detection(
  @reader_1_id,
  @observe1_id,
  @observe2_id,
  @observe3_id
);

