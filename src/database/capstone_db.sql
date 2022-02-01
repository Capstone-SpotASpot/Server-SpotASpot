-- Capstone Database Creation Code

-- TODO: change this
DROP DATABASE IF EXISTS capstone;

CREATE DATABASE IF NOT EXISTS capstone;

USE capstone;

DROP TABLE IF EXISTS readers;
CREATE TABLE readers
(
    reader_id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    reader_x_coord FLOAT NOT NULL,
    reader_y_coord FLOAT NOT NULL
);

INSERT INTO readers (reader_x_coord, reader_y_coord)
    VALUES (0.0, 0.0), (1.0, 1.0)
