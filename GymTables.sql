USE ecom;

CREATE TABLE members (
id int AUTO_INCREMENT PRIMARY KEY,
member_name VARCHAR(75) NOT NULL
);


CREATE TABLE workouts(
id INT AUTO_INCREMENT PRIMARY KEY,
type_workout VARCHAR(150) NOT NULL,
duration VARCHAR(150) NULL,
members_id INT,
FOREIGN KEY (members_id) REFERENCES members(id)
);