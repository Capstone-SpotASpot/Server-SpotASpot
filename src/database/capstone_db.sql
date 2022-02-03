-- SpotASpot Database Creation Code

DROP DATABASE IF EXISTS SpotASpot_dev;

CREATE DATABASE IF NOT EXISTS SpotASpot_dev;

USE SpotASpot_dev;

DROP TABLE IF EXISTS readers;

CREATE TABLE readers
(
    reader_id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    latitude FLOAT( 10, 6 ) NOT NULL,
    longitude FLOAT( 10, 6 ) NOT NULL
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
  IN p_latitude FLOAT( 10, 6 ),
  IN p_longitude FLOAT( 10, 6 )
) BEGIN

    INSERT INTO readers (reader_id, latitude, longitude )
        VALUES (DEFAULT, p_latitude, p_longitude );

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

-- ###### End of Procedures ######

-- ###### Start of Functions ######

-- ###### End of Functions ######


INSERT INTO readers (longitude, latitude)
    VALUES (0.0, 0.0), (1.0, 1.0)
