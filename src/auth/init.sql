CREATE USER 'auth_user'@'localhost' IDENTIFIED BY 'Aauth123'; #user access the mysqldb

CREATE DATABASE auth; #create database

GRANT ALL PRIVILEGES ON auth.* TO 'auth_user'@'localhost';

USE auth;

CREATE TABLE user(
	id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	email VARCHAR(255) NOT NULL UNIQUE,
	password VARCHAR(255) NOT NULL
);

INSERT INTO user (email, password) VALUES ('txin@uchicago.edu', 'Admin123');
