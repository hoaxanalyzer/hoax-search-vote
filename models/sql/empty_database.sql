CREATE TABLE log_query (
`id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
`log_hash` TEXT NOT NULL,
`query_text` TEXT NOT NULL,
`query_search` TEXT NOT NULL,
`query_hash` TEXT NOT NULL,
`query_time` DATETIME NOT NULL,
`client_ip` VARCHAR(50) NOT NULL,
`client_browser` TEXT NULL,
`clicked` INT NOT NULL
);

CREATE TABLE log_result (
`id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
`id_query` INT NOT NULL,
`finished_at` DATETIME NOT NULL,
`hoax_score` FLOAT NOT NULL,
`fact_score` FLOAT NOT NULL,
`unknown_score` FLOAT NOT NULL,
`unrelated_score` FLOAT NOT NULL,
`conclusion` VARCHAR(20) NOT NULL,
`developer_notes` TEXT NULL
);

CREATE TABLE feedback_result (
`id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
`query_hash` TEXT NOT NULL,
`reported_at` DATETIME NOT NULL,
`is_know` VARCHAR(20) NOT NULL,
`reason` TEXT NOT NULL,
`feedback_label` VARCHAR(20) NOT NULL,
`client_ip` VARCHAR(50) NOT NULL,
`client_browser` TEXT NULL
);

CREATE TABLE feedback_reference (
`id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
`article_hash` TEXT NOT NULL,
`reported_at` DATETIME NOT NULL,
`is_relevant` VARCHAR(20) NOT NULL,
`reason` TEXT NOT NULL,
`feedback_label` VARCHAR(20) NOT NULL,
`client_ip` VARCHAR(50) NOT NULL,
`client_browser` TEXT NULL
);

CREATE TABLE query_dictionary (
`id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
`hash` TEXT NOT NULL,
`text` TEXT NULL,
`query` TEXT NOT NULL,
`entities` TEXT NULL,
`topics` TEXT NULL
);

CREATE TABLE article_reference (
`id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
`id_query` INT NOT NULL,
`query_hash` TEXT NOT NULL,
`article_hash` TEXT NULL,
`article_date` VARCHAR(20) NULL,
`article_url` TEXT NOT NULL,
`article_content` LONGTEXT NOT NULL,
`retrieved_at` DATETIME NOT NULL
);


