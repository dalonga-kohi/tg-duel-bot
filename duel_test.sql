-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Wrz 13, 2024 at 11:26 PM
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

INSERT INTO `accounts` (`user_id`, `pub_key`, `priv_key`, `won`, `lost`, `total`, `withdraw`) VALUES
('1121843738', '7jUmJChptzfZaf52JXZG5AE3pwNn9m4eMh3H55s9MBjN', '58ee8fa97e6f28b41eed2ee720f335e9ef5d084ca25de87a172365b7e2780bf9', 0, 0, 0, 0),
('1192519309', '149oXVuiieSV5SEG6Kh84CevUgEAiRbL6Vn4Vyq9bCTJ', '7187d68b8a739a4750837bec1601ab6809cc78dfc9f516ac9ae7e0e53f5cc574', 0, 0, 0, 0),
('1629621888', '431aqnhtCX1oMSh4m1Q1RRhGCr94pAEsZj99EfF94kMm', 'bf3482c4a4ca5c340f628ff273ab94db645b42742a21226aae6136ed651ee7eb', 0, 0, 0, 0),
('1898387981', 'CbUrRkUd92EG1qBUQvKKgHu3uEPFVnP1UAK6Jc9a1hr6', '6b6f37b2f6b912b528eea3957c271c83fd573ca3fdd3ed30ec1ce3f24606760c', 1, 0, 49250, 0),
('5726103959', 'EtueL1hUGdNiDCJ71vtFHsAw873y7wEHk8qSvAMSePfU', '961285fb6a5c919b0077b60e2e91e5ae70f84ed2ec449a1aef9229a53d5e83c1', 0, 0, 0, 0),
('5836629497', '2d5JjsjK3MdtvaQCtuKeSoBxxQ9jDijEdbNUhbCUGHyH', 'a4c63af01067483abd8803c8fce1f44c5451cb33491798f94ca1ebace014a194', 0, 0, 0, 0),
('6068073472', 'D9R9UKqQRQ3VqXZawf7ojHkmY4D4Bo1aPG9z53T8eDjr', 'ad1d99e7f13bed6052aa9dfe6685e3af5727c65edbfcfe22c6458df8128501cd', 0, 0, 0, 0),
('6299879619', 'EaLPmHHTfd1i3zv6rmkNZNVp36J81QxZPuQLepCt9Rje', 'b58b8c52dd963dfe64245d857ae53c68b8d97985d968e54de12fc77c0d53a52b', 0, 0, 0, 0),
('6662625606', '6C5ykBEEx7uxuHTZsPY8u4rSUos1GJyLCBrnZyu6edTy', 'c6b27d513ed6fd967ff9c56e8b7e260f81c11c29a846f686578f3f11e6871f39', 0, 1, 0, 0),
('6746721935', 'DXbXF873DGC24bZd7dhXdpjYoovnj3yh55SDdu27m9Sf', '855759010778278734ed481149ae363e750bbf3d24eb49a9a58bab8e0bf842c3', 1, 0, 246250, 0),
('6856958352', 'CmihpCCZRP2kZBKFG4k18Ue7pHR2jgx55rq7UHHyVvJq', 'c3f432246ecb213c203eddb5ebc220cba8d8b9497becd1645384759af95d7c4a', 0, 2, 0, 0),
('7004752564', 'GZRPEbwdMZ5jiHbdYHFG8Q3Xd3Ep45gkYUM243aaX4AP', '0434e566dd4da1316101c8c6a9af8188a41db7ed87c620b356e1c5d6727f5169', 0, 1, 0, 0),
('7088758967', 'rTFfVWHe6cfgqo9isQ3W9RhFhNJ3UEeeerGNBGJ8RDD', '22401dc24bf957fbbac3b6c1540795389638e94c405dd169bd4c5ebfeb5cb846', 1, 0, 90000, 90000),
('7137059578', 'qczLqUN9wwhe5zEjRkaEQMvvuVnKwWKZG4aZWUwFoQk', '596f11f774ab964eed8d67c5662b9ab54f152850919dfdb1955835bf102e272a', 0, 0, 0, 0),
('7280551786', '9F2NJnUu58ZPx9q7K6EL6zTwv8BSxKev6oWShY3HCrXA', '74ba18582480cde4bcff3c81c68f94521ffc87dc156c198504c1a0fb3bf05182', 0, 0, 0, 0),
('7496878788', 'HutPthWVWuSJQFuJCcDisL23spFKuzSswPPMgiEWTwSt', '5b514274876f0eef885d4affd25061fb18a42f2c9b61dd1f7cdc23bcc776789b', 0, 0, 0, 0);

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
  `winner` varchar(12) DEFAULT NULL,
  `date` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `games`
--

INSERT INTO `games` (`game_id`, `p1`, `p2`, `p3`, `p4`, `p5`, `stake`, `status`, `winner`, `date`) VALUES
(3739630, '7280551786', NULL, '6341657896', '1121843738', NULL, '20000', 1, NULL, '2024-09-13 22:12:10'),
(3997038, '7122889711', '6068073472', '6856958352', '7088758967', '6662625606', '20000', 3, '7088758967', '2024-09-13 22:12:10'),
(5426925, '7004752564', '6746721935', '7122889711', '7136319503', '7329817721', '50000', 3, '6746721935', '2024-09-13 22:12:10'),
(6481869, '6068073472', '1898387981', '6299879619', '7496878788', '6662625606', '10000', 3, '1898387981', '2024-09-13 22:12:10'),
(9764607, '1358086891', NULL, NULL, NULL, NULL, '50000', 9, NULL, '2024-09-13 22:12:10');

-- --------------------------------------------------------

--
-- Struktura tabeli dla tabeli `wallets`
--

CREATE TABLE `wallets` (
  `user_id` varchar(12) NOT NULL,
  `game_id` int(11) NOT NULL,
  `pub_key` varchar(64) NOT NULL,
  `priv_key` varchar(70) NOT NULL,
  `date` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `wallets`
--

INSERT INTO `wallets` (`user_id`, `game_id`, `pub_key`, `priv_key`, `date`) VALUES
('1121843738', 3739630, '3M6yiBhrL4yk1kY5FHbEhNbhkifmus3N1L7P5Ps8Jx31', 'fc77419faf5b4c46d52b05bdf3c6f1fb8820110c380ab52032b32679dad07bcd', '2024-09-13 22:24:08'),
('1358086891', 9764607, 'FPsNGQ7SJKrEfdWbzUQS1mTh7GidugMFVu9Zs18ZMggY', '8fdb3d15d873aaadfe84bd6893008a611471dc0e3529bb8e5e3824d256ecfcec', '2024-09-13 22:24:08'),
('1898387981', 6481869, 'HotZ4TAPiDLNKijiRcvyiwBy32QXeYEaFtbV51SxmaL2', 'c15ae09c760cde7a45b0b60192489b1cf1aebb706dc937d3a55716b895abd77a', '2024-09-13 22:24:08'),
('6068073472', 3997038, '31W8prnsuxSWWVb9BPiBCbBTzqbZMgykHii1wtNcbDLs', '086b232dd437daae33b51c6499a8ae77e6894f74d5ab98047cab5faaa788f280', '2024-09-13 22:24:08'),
('6068073472', 6481869, '5acUykJch4ZFsJSNhExFFgcLfvGW7hDkn7wh6p9dnGtX', '8bcb74fb7c20eddf0cb8ab61948d154df0dc30edbdcab5b40eba83b2120d2e6d', '2024-09-13 22:24:08'),
('6299879619', 6481869, '872oExbstigUmgQvSbNXu9dAXGyzUDDwfKXYbyKfGfye', '9d2411098571e71c5c0683228148a9c3bc45997a5f0cb7e52d3955c1d9d2b85b', '2024-09-13 22:24:08'),
('6341657896', 3739630, '4K7ZVnVuMi3p6JzYn922sB3c1ye3Qgp9x6c6G8a4wsqz', 'ef12044e8807ebcaa678d9cdc290142fb29215b6a8f3679ae7a5d8e5586f2d46', '2024-09-13 22:24:08'),
('6662625606', 3997038, 'GRo3zXKSpfnNY7Dj9DxMWdR1SHPxuzTwzxRG78ZVYtmW', '7f51431d40c6d63e1c150ba52b4e6fed5fc6571147f37adcc26c8872f94f7284', '2024-09-13 22:24:08'),
('6662625606', 6481869, 'H9CuagAUpMFdVnt6komwsJajz6a83FmWrZ4G3MwAnC3', 'cf0b638b6961ebda1d365380097eabf94670755c9916563a28a7b0dc16bd050c', '2024-09-13 22:24:08'),
('6746721935', 5426925, 'JDuZQ74hCR1g7rgXpgxgAGmWW5My7yYLtxZT8hZjUFZA', 'fef370daf63e05262dd83e250cf1c01745f8452e334aa5e0f06b8850d0b68e56', '2024-09-13 22:24:08'),
('6856958352', 3997038, 'duGWDR4yzB5EauzJVNwwF7AyXouNo99enxS5yhvUA2e', 'b8e8503921cbf6d4ddfc21394f2944c94eb2cbc843a0fd4770c35007e5bff498', '2024-09-13 22:24:08'),
('7004752564', 5426925, '6wzXscpUibPy7oLjtP4YjQPnCRKssuWCR8M1oWFCSxn8', 'c05060544d5cea8c4cc688be068941b1d469c813b7671b77b725f87f48fc3d7f', '2024-09-13 22:24:08'),
('7088758967', 3997038, '3nkRbKxt4fi5xFqVP8ZjgqVktGNsbyMDxkLYA2fApDhh', 'a84a30b1fbee2c089d5b764575f5f87475a5d6b72aefad2df629d2dcdd21ecb7', '2024-09-13 22:24:08'),
('7122889711', 3997038, 'DMmh6bpHxLXSpB5BsEgubKfWEoE6ETYg8hpusGMuT28f', 'ce561e3f19fc0108da26f52edf619c2bce69321e38012e5fb0c21ca9906e1c04', '2024-09-13 22:24:08'),
('7122889711', 5426925, 'Cfqw9jku415Bu1WdSCvbpMcxQf4v7sfSgkXmmuoCJaFm', 'e833fad65f3686d38de33b09b33b90e5d78bdfaf2ef5f65bf273e1a5782c3221', '2024-09-13 22:24:08'),
('7136319503', 5426925, 'BwVzj6rzMn5tGFkGpBgHRsVHsbL9Y4QJ8hU9fKmjs4LY', 'e35a1da2d3ac130109aacc72dacd005ca1f60b0fa9eb299f8288adf32a97578f', '2024-09-13 22:24:08'),
('7280551786', 3739630, 'CCqQARQQMqoxAe2hHLdUDjpAwXjzj4DwW4Nk3N596Qss', 'a4f0f1183dd5c0035b48a6a978801b4444b3de5a11e27d9ce16621bc0619621b', '2024-09-13 22:24:08'),
('7329817721', 5426925, '2SRTZ4hTydYgTsVkhDu8hkJSoBEiVt9NSDx79CmAMFDw', '380fc2e1e45720ba8a9d118a6136d3669a639636654eae9305fe601bb9f8057a', '2024-09-13 22:24:08'),
('7496878788', 6481869, 'Ewox1qv3nQRyraXkUUTrPbB1ee67Ap2fPkGjmomWPiuF', 'b91ce508708b41570f9536f75658d475b0fd4507e551c8b9376090e73ebbf8a8', '2024-09-13 22:24:08');

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
