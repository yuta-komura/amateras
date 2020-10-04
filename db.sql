-- データベース
CREATE DATABASE tradingbot;

-- テーブル
CREATE TABLE `entry` (
    `process_id` int NOT NULL AUTO_INCREMENT,
    `date` timestamp(6) NOT NULL,
    `side` varchar(255) NOT NULL,
    `price` int unsigned NOT NULL,
    PRIMARY KEY (`process_id`)
) ENGINE = InnoDB AUTO_INCREMENT = 2 DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;

CREATE TABLE `position` (
    `side` varchar(255) NOT NULL,
    `size` float NOT NULL
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;

CREATE TABLE `child_order` (
    `id` int NOT NULL AUTO_INCREMENT,
    `date` datetime(6) NOT NULL,
    `side` varchar(255) DEFAULT NULL,
    `price` int unsigned DEFAULT NULL,
    `size` float unsigned DEFAULT NULL,
    `event_type` varchar(255) NOT NULL,
    `child_order_type` varchar(255) DEFAULT NULL,
    `product_code` varchar(255) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;

CREATE TABLE `execution_history` (
    `id` int NOT NULL AUTO_INCREMENT,
    `date` datetime(6) NOT NULL,
    `side` varchar(255) NOT NULL,
    `price` int unsigned NOT NULL,
    `size` float unsigned NOT NULL,
    PRIMARY KEY (`id`),
    KEY `index_execution_history_1` (`date`)
) ENGINE = InnoDB AUTO_INCREMENT = 18045589 DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;

CREATE TABLE `ticker` (
    `date` timestamp NOT NULL,
    `best_bid` int unsigned NOT NULL,
    `best_ask` int unsigned NOT NULL
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;

insert into
    ticker
values
    (now(), 0, 0);