DROP TABLE IF EXISTS devices;
DROP TABLE IF EXISTS data;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS sessions;
CREATE TABLE devices (
    mac_address VARCHAR(255) PRIMARY KEY
);
CREATE TABLE data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mac_address VARCHAR(255) NOT NULL,
    pixels JSON NOT NULL,
    thermistor_temp FLOAT NOT NULL,
    prediction VARCHAR(255) NOT NULL,
    confidence VARCHAR(255) NOT NULL,
    CONSTRAINT fk_refer FOREIGN KEY (mac_address) references devices(mac_address));

CREATE TABLE users(
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL);

CREATE TABLE sessions(
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    session_token VARCHAR(255) NOT NULL,
    CONSTRAINT fk_refer2 FOREIGN KEY (user_id) references users(id));



