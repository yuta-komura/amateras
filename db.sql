-- データベース
CREATE DATABASE tradingbot;

-- テーブル
CREATE TABLE `bitflyer_btc_ohlc_1M` (
    `Date` datetime(6) NOT NULL,
    `Open` int unsigned NOT NULL,
    `High` int unsigned NOT NULL,
    `Low` int unsigned NOT NULL,
    `Close` int unsigned NOT NULL,
    `Volume` decimal(65, 30) unsigned NOT NULL,
    PRIMARY KEY (`Date`)
);

CREATE TABLE `backtest_entry` (
    `date` timestamp NOT NULL,
    `side` varchar(255) NOT NULL,
    `price` int unsigned NOT NULL,
    `size` float unsigned NOT NULL
);

CREATE TABLE `entry` (`side` varchar(255) NOT NULL);

CREATE TABLE `execution_history` (
    `id` bigint unsigned NOT NULL AUTO_INCREMENT,
    `date` datetime(6) NOT NULL,
    `side` varchar(255) NOT NULL,
    `price` int unsigned NOT NULL,
    `size` decimal(65, 30) unsigned NOT NULL,
    PRIMARY KEY (`id`),
    KEY `index_execution_history_1` (`date`)
);

CREATE TABLE `ticker` (
    `date` timestamp NOT NULL,
    `best_bid` int unsigned NOT NULL,
    `best_ask` int unsigned NOT NULL
);