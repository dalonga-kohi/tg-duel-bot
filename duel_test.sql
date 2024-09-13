-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Wrz 13, 2024 at 08:43 PM
-- Wersja serwera: 10.4.32-MariaDB
-- Wersja PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `duel_test`
--

-- --------------------------------------------------------

--
-- Struktura tabeli dla tabeli `accounts`
--

CREATE TABLE `accounts` (
  `user_id` varchar(12) NOT NULL,
  `pub_key` varchar(64) NOT NULL,
  `priv_key` varchar(70) NOT NULL,
  `won` int(11) NOT NULL DEFAULT 0,
  `lost` int(11) NOT NULL DEFAULT 0,
  `total` int(11) NOT NULL DEFAULT 0,
  `withdraw` float NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `accounts`
--

-- --------------------------------------------------------

--
-- Struktura tabeli dla tabeli `config`
--

CREATE TABLE `config` (
  `name` varchar(20) NOT NULL,
  `pub_key` varchar(72) DEFAULT NULL,
  `priv_key` varchar(72) DEFAULT NULL,
  `val` varchar(80) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `config`
--

INSERT INTO `config` (`name`, `pub_key`, `priv_key`, `val`) VALUES
('fee1', '26e7tht6dNQ2SZECuSsJVFHoNzBh5XyrUXttqDyCjhaQ', NULL, '0.0125'),
('fee2', '5QbT99Z8HfpDC6Jm8qJpPrNkYS2W8rDoKiC4a37MTtHc', NULL, '0.0025'),
('payer', NULL, '583bc2e6fa0a84c881e5ae21a3a74c213e2ced902b3be64b268a3d007cd9ee9a', NULL),
('vault', '2JLM5dd7VXL1dVoToM2vUP3DwyvTVtnatTeGDwLumx6u', 'ffdd857f2960105b5605066aabe6dc29262f3c724485139c8893e82e0fb07e6e', '');

-- --------------------------------------------------------

--
-- Struktura tabeli dla tabeli `games`
--

CREATE TABLE `games` (
  `game_id` int(11) NOT NULL,
  `p1` varchar(12) NOT NULL,
  `p2` varchar(12) DEFAULT NULL,
  `p3` varchar(12) DEFAULT NULL,
  `p4` varchar(12) DEFAULT NULL,
  `p5` varchar(12) DEFAULT NULL,
  `stake` varchar(15) NOT NULL,
  `status` int(11) NOT NULL DEFAULT 9,
  `winner` varchar(12) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `games`
--

-- --------------------------------------------------------

--
-- Struktura tabeli dla tabeli `wallets`
--

CREATE TABLE `wallets` (
  `user_id` varchar(12) NOT NULL,
  `game_id` int(11) NOT NULL,
  `pub_key` varchar(64) NOT NULL,
  `priv_key` varchar(70) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `wallets`
--

--
-- Indeksy dla zrzutów tabel
--

--
-- Indeksy dla tabeli `accounts`
--
ALTER TABLE `accounts`
  ADD PRIMARY KEY (`user_id`);

--
-- Indeksy dla tabeli `config`
--
ALTER TABLE `config`
  ADD PRIMARY KEY (`name`);

--
-- Indeksy dla tabeli `games`
--
ALTER TABLE `games`
  ADD PRIMARY KEY (`game_id`);

--
-- Indeksy dla tabeli `wallets`
--
ALTER TABLE `wallets`
  ADD PRIMARY KEY (`user_id`,`game_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
