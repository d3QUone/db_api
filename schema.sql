CREATE TABLE 'Forum_t' (
	'id' INT AUTO_INCREMENT,
	'short_name' VARCHAR(100) NOT NULL,
	'name' VARCHAR(100) NOT NULL,
	'user' VARCHAR(100) NOT NULL,
	'isDeleted' BOOLEAN DEFAULT TRUE,
	PRIMARY KEY('short_name')
);


