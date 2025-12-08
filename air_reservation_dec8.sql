-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Dec 08, 2025 at 12:30 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `air_reservation`
--

-- --------------------------------------------------------

--
-- Table structure for table `agent_airline_authorization`
--

CREATE TABLE `agent_airline_authorization` (
  `agent_email` varchar(50) NOT NULL,
  `airline_name` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `agent_airline_authorization`
--

INSERT INTO `agent_airline_authorization` (`agent_email`, `airline_name`) VALUES
('agent1@example.com', 'agentAirline1'),
('agent1@example.com', 'DemoAir1'),
('agent3@example.com', 'DemoAir1');

-- --------------------------------------------------------

--
-- Table structure for table `airline`
--

CREATE TABLE `airline` (
  `airline_name` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `airline`
--

INSERT INTO `airline` (`airline_name`) VALUES
('agentAirline1'),
('DemoAir1'),
('NYAir');

-- --------------------------------------------------------

--
-- Table structure for table `airline_staff`
--

CREATE TABLE `airline_staff` (
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `date_of_birth` date NOT NULL,
  `airline_name` varchar(50) NOT NULL,
  `role` enum('staff','admin','operator','both') DEFAULT 'admin'
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- --------------------------------------------------------

--
-- Table structure for table `airplane`
--

CREATE TABLE `airplane` (
  `airline_name` varchar(50) NOT NULL,
  `airplane_id` int(11) NOT NULL,
  `seat_capacity` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `airplane`
--

INSERT INTO `airplane` (`airline_name`, `airplane_id`, `seat_capacity`) VALUES
('agentAirline1', 1, 150),
('DemoAir1', 1, 10),
('DemoAir1', 2, 180),
('NYAir', 1, 180);

-- --------------------------------------------------------

--
-- Table structure for table `airport`
--

CREATE TABLE `airport` (
  `airport_name` varchar(50) NOT NULL,
  `airport_city` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `airport`
--

INSERT INTO `airport` (`airport_name`, `airport_city`) VALUES
('ORD', 'Chicago'),
('LAX', 'Los Angeles'),
('LGA', 'New York'),
('JFK', 'New York City');

-- --------------------------------------------------------

--
-- Table structure for table `booking_agent`
--

CREATE TABLE `booking_agent` (
  `email` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `booking_agent`
--

INSERT INTO `booking_agent` (`email`, `password`) VALUES
('agent1@example.com', 'scrypt:32768:8:1$VMfYK6eyR7hv6M2x$4c3d9087865ec2c920c5e071b262ce481d7917913bfe2a8a67854b9c07f96d05b44fc5245c2005254441e66a0fbfd75177b64b1076e1bde1d405a02ebe78fb9d'),
('agent2@example.com', 'scrypt:32768:8:1$IQe6q6s7FKD6aUsQ$9ce7556efee7c4f2f3e1b1edfa1dd1bcd15a7de14ac6e78a6fa7ed24d7835be74ba2677d5cd8b2062adf60575d15d0828de625c22e9cdd553597d77c0791873c'),
('agent3@example.com', 'scrypt:32768:8:1$KcCZAXLZmYO5fixu$03d827e75f6ef096d114331fa898c08cbec943fb0c90a704fdbf50ab72991adce06df982ac1430273d7f6e0ef17696f4f6dce81ab6e98fa2b4f662b209d76be5');

-- --------------------------------------------------------

--
-- Table structure for table `city`
--

CREATE TABLE `city` (
  `city_name` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `city`
--

INSERT INTO `city` (`city_name`) VALUES
('Chicago'),
('Los Angeles'),
('New York'),
('New York City');

-- --------------------------------------------------------

--
-- Table structure for table `customer`
--

CREATE TABLE `customer` (
  `email` varchar(50) NOT NULL,
  `name` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `building_number` varchar(30) NOT NULL,
  `street` varchar(30) NOT NULL,
  `city` varchar(30) NOT NULL,
  `state` varchar(30) NOT NULL,
  `phone_number` varchar(20) NOT NULL,
  `passport_number` varchar(30) NOT NULL,
  `passport_expiration` date NOT NULL,
  `passport_country` varchar(50) NOT NULL,
  `date_of_birth` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `customer`
--

INSERT INTO `customer` (`email`, `name`, `password`, `building_number`, `street`, `city`, `state`, `phone_number`, `passport_number`, `passport_expiration`, `passport_country`, `date_of_birth`) VALUES
('1@mail.com', '123', 'scrypt:32768:8:1$TJoQe3dxEGJ7pmRv$67dbafdeb6fce11963965ce750da19009430b1751e9adf5f9cf93d4b0608f91bd9e0deff993a6f9c807bd67a1238b1e0d799cf1b9d89de2b4919df1e6ad5967b', '123', '1', '2', '3', '1231231123', '123123123', '2011-11-11', '111111111', '2010-11-12'),
('alice@example.com', 'Alice Demo', 'scrypt:32768:8:1$imXcCHsHUvg8ZPZg$d34b8914160c8aa9f28b5804f5eb5a2097d5e8e65857a54d28b87de003734aae79f08f6bfc618a7a79a2d53d47aaea001019a964d41002f31cda9e396a73dae3', '123', 'Main St', 'New York', 'NY', '123-456-7890', 'P1234567', '2030-01-01', 'USA', '1990-05-10'),
('nycustomer@example.com', 'NY Customer', 'scrypt:32768:8:1$oPeSWscz8jhjz1NH$e066fd5c6d7f8ae9de3d5e74f1701ec8a7c98b8d4a7312b4d651aa5a55f71a2e35d78763f12f2a60c5131ba43c7cad52e4230caf3cb37bf22746e197ecd10e47', '10', 'Queens Blvd', 'New York', 'NY', '555-000-0000', 'P0000001', '2030-01-01', 'USA', '1990-01-01');

-- --------------------------------------------------------

--
-- Table structure for table `flight`
--

CREATE TABLE `flight` (
  `airline_name` varchar(50) NOT NULL,
  `flight_num` int(11) NOT NULL,
  `departure_airport` varchar(50) NOT NULL,
  `departure_time` datetime NOT NULL,
  `arrival_airport` varchar(50) NOT NULL,
  `arrival_time` datetime NOT NULL,
  `price` decimal(10,0) NOT NULL,
  `status` enum('upcoming','in-progress','delayed') DEFAULT 'upcoming',
  `airplane_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `flight`
--

INSERT INTO `flight` (`airline_name`, `flight_num`, `departure_airport`, `departure_time`, `arrival_airport`, `arrival_time`, `price`, `status`, `airplane_id`) VALUES
('agentAirline1', 4101, 'LGA', '2025-12-20 09:00:00', 'LAX', '2025-12-20 12:00:00', 350, 'upcoming', 1),
('agentAirline1', 4102, 'LAX', '2025-12-22 15:00:00', 'JFK', '2025-12-22 23:00:00', 360, 'upcoming', 1),
('agentAirline1', 4103, 'ORD', '2025-08-10 08:00:00', 'LGA', '2025-08-10 11:00:00', 220, 'in-progress', 1),
('DemoAir1', 101, 'JFK', '2025-01-01 10:00:00', 'LAX', '2025-01-01 13:00:00', 350, 'upcoming', 1),
('DemoAir1', 1001, 'JFK', '2025-12-20 10:00:00', 'LAX', '2025-12-20 13:00:00', 300, 'upcoming', 1),
('DemoAir1', 1002, 'LAX', '2025-09-10 09:00:00', 'JFK', '2025-09-10 17:00:00', 250, 'delayed', 1),
('DemoAir1', 1003, 'JFK', '2025-03-05 08:00:00', 'LAX', '2025-03-05 11:00:00', 220, 'in-progress', 1),
('DemoAir1', 3001, 'JFK', '2025-12-20 09:00:00', 'ORD', '2025-12-20 11:00:00', 250, 'upcoming', 1),
('DemoAir1', 3002, 'ORD', '2025-12-22 14:00:00', 'LGA', '2025-12-22 17:00:00', 230, 'upcoming', 1),
('DemoAir1', 3003, 'LGA', '2025-08-10 08:00:00', 'JFK', '2025-08-10 08:45:00', 120, 'in-progress', 1),
('DemoAir1', 4001, 'JFK', '2025-12-26 09:00:00', 'LAX', '2025-12-26 12:00:00', 320, 'upcoming', 1),
('DemoAir1', 4002, 'LAX', '2025-12-27 13:00:00', 'JFK', '2025-12-27 21:00:00', 310, 'upcoming', 1),
('DemoAir1', 4003, 'JFK', '2025-12-28 08:30:00', 'ORD', '2025-12-28 10:30:00', 210, 'upcoming', 1),
('DemoAir1', 4004, 'ORD', '2025-12-29 15:00:00', 'LGA', '2025-12-29 17:30:00', 190, 'upcoming', 1),
('NYAir', 2001, 'LGA', '2025-12-20 09:00:00', 'ORD', '2025-12-20 11:00:00', 220, 'upcoming', 1),
('NYAir', 2002, 'JFK', '2025-12-22 14:00:00', 'LGA', '2025-12-22 14:45:00', 120, 'upcoming', 1),
('NYAir', 2003, 'LGA', '2025-08-10 08:00:00', 'JFK', '2025-08-10 08:30:00', 90, 'in-progress', 1);

-- --------------------------------------------------------

--
-- Table structure for table `purchases`
--

CREATE TABLE `purchases` (
  `ticket_id` int(11) NOT NULL,
  `customer_email` varchar(50) NOT NULL,
  `booking_agent_email` varchar(50) DEFAULT NULL,
  `purchase_date` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `purchases`
--

INSERT INTO `purchases` (`ticket_id`, `customer_email`, `booking_agent_email`, `purchase_date`) VALUES
(1, '1@mail.com', NULL, '2025-12-06'),
(2, '1@mail.com', NULL, '2025-12-07'),
(3, 'alice@example.com', NULL, '2025-10-10'),
(4, 'alice@example.com', NULL, '2025-08-05'),
(5, 'alice@example.com', NULL, '2025-04-20'),
(6, 'alice@example.com', NULL, '2024-10-01'),
(7, 'alice@example.com', NULL, '2025-12-01'),
(8, 'alice@example.com', NULL, '2025-11-15'),
(9, 'alice@example.com', 'agent1@example.com', '2025-12-08'),
(1001, 'nycustomer@example.com', NULL, '2025-11-15'),
(1002, 'nycustomer@example.com', NULL, '2025-10-05'),
(1003, 'nycustomer@example.com', NULL, '2025-07-01'),
(2001, 'alice@example.com', 'agent1@example.com', '2025-11-15'),
(2002, 'alice@example.com', 'agent1@example.com', '2025-12-01'),
(3101, 'alice@example.com', 'agent1@example.com', '2025-11-30'),
(3102, 'nycustomer@example.com', 'agent1@example.com', '2025-12-01'),
(3103, 'alice@example.com', 'agent1@example.com', '2025-09-01'),
(3104, 'alice@example.com', NULL, '2025-12-08');

-- --------------------------------------------------------

--
-- Table structure for table `ticket`
--

CREATE TABLE `ticket` (
  `ticket_id` int(11) NOT NULL,
  `airline_name` varchar(50) NOT NULL,
  `flight_num` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `ticket`
--

INSERT INTO `ticket` (`ticket_id`, `airline_name`, `flight_num`) VALUES
(9, 'agentAirline1', 4101),
(3101, 'agentAirline1', 4101),
(3102, 'agentAirline1', 4102),
(3103, 'agentAirline1', 4103),
(1, 'DemoAir1', 101),
(2, 'DemoAir1', 101),
(3, 'DemoAir1', 101),
(7, 'DemoAir1', 1001),
(8, 'DemoAir1', 1001),
(4, 'DemoAir1', 1002),
(5, 'DemoAir1', 1003),
(6, 'DemoAir1', 1003),
(2001, 'DemoAir1', 3001),
(2004, 'DemoAir1', 3001),
(2002, 'DemoAir1', 3002),
(2003, 'DemoAir1', 3003),
(3104, 'DemoAir1', 4004),
(1001, 'NYAir', 2001),
(1002, 'NYAir', 2002),
(1003, 'NYAir', 2003);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `agent_airline_authorization`
--
ALTER TABLE `agent_airline_authorization`
  ADD PRIMARY KEY (`agent_email`,`airline_name`),
  ADD KEY `airline_name` (`airline_name`);

--
-- Indexes for table `airline`
--
ALTER TABLE `airline`
  ADD PRIMARY KEY (`airline_name`);

--
-- Indexes for table `airline_staff`
--
ALTER TABLE `airline_staff`
  ADD PRIMARY KEY (`username`),
  ADD KEY `airline_name` (`airline_name`);

--
-- Indexes for table `airplane`
--
ALTER TABLE `airplane`
  ADD PRIMARY KEY (`airline_name`,`airplane_id`);

--
-- Indexes for table `airport`
--
ALTER TABLE `airport`
  ADD PRIMARY KEY (`airport_name`),
  ADD KEY `fk_airport_city` (`airport_city`);

--
-- Indexes for table `booking_agent`
--
ALTER TABLE `booking_agent`
  ADD PRIMARY KEY (`email`);

--
-- Indexes for table `city`
--
ALTER TABLE `city`
  ADD PRIMARY KEY (`city_name`);

--
-- Indexes for table `customer`
--
ALTER TABLE `customer`
  ADD PRIMARY KEY (`email`);

--
-- Indexes for table `flight`
--
ALTER TABLE `flight`
  ADD PRIMARY KEY (`airline_name`,`flight_num`),
  ADD KEY `airline_name` (`airline_name`,`airplane_id`),
  ADD KEY `departure_airport` (`departure_airport`),
  ADD KEY `arrival_airport` (`arrival_airport`);

--
-- Indexes for table `purchases`
--
ALTER TABLE `purchases`
  ADD PRIMARY KEY (`ticket_id`,`customer_email`),
  ADD KEY `booking_agent_email` (`booking_agent_email`),
  ADD KEY `customer_email` (`customer_email`);

--
-- Indexes for table `ticket`
--
ALTER TABLE `ticket`
  ADD PRIMARY KEY (`ticket_id`),
  ADD KEY `airline_name` (`airline_name`,`flight_num`);

--
-- Constraints for dumped tables
--

--
-- Constraints for table `agent_airline_authorization`
--
ALTER TABLE `agent_airline_authorization`
  ADD CONSTRAINT `agent_airline_authorization_ibfk_1` FOREIGN KEY (`agent_email`) REFERENCES `booking_agent` (`email`) ON DELETE CASCADE,
  ADD CONSTRAINT `agent_airline_authorization_ibfk_2` FOREIGN KEY (`airline_name`) REFERENCES `airline` (`airline_name`) ON DELETE CASCADE;

--
-- Constraints for table `airline_staff`
--
ALTER TABLE `airline_staff`
  ADD CONSTRAINT `airline_staff_ibfk_1` FOREIGN KEY (`airline_name`) REFERENCES `airline` (`airline_name`) ON DELETE CASCADE;

--
-- Constraints for table `airplane`
--
ALTER TABLE `airplane`
  ADD CONSTRAINT `airplane_ibfk_1` FOREIGN KEY (`airline_name`) REFERENCES `airline` (`airline_name`) ON DELETE CASCADE;

--
-- Constraints for table `airport`
--
ALTER TABLE `airport`
  ADD CONSTRAINT `fk_airport_city` FOREIGN KEY (`airport_city`) REFERENCES `city` (`city_name`);

--
-- Constraints for table `flight`
--
ALTER TABLE `flight`
  ADD CONSTRAINT `flight_ibfk_1` FOREIGN KEY (`airline_name`,`airplane_id`) REFERENCES `airplane` (`airline_name`, `airplane_id`),
  ADD CONSTRAINT `flight_ibfk_2` FOREIGN KEY (`departure_airport`) REFERENCES `airport` (`airport_name`),
  ADD CONSTRAINT `flight_ibfk_3` FOREIGN KEY (`arrival_airport`) REFERENCES `airport` (`airport_name`);

--
-- Constraints for table `purchases`
--
ALTER TABLE `purchases`
  ADD CONSTRAINT `purchases_ibfk_1` FOREIGN KEY (`ticket_id`) REFERENCES `ticket` (`ticket_id`),
  ADD CONSTRAINT `purchases_ibfk_2` FOREIGN KEY (`booking_agent_email`) REFERENCES `booking_agent` (`email`),
  ADD CONSTRAINT `purchases_ibfk_3` FOREIGN KEY (`customer_email`) REFERENCES `customer` (`email`);

--
-- Constraints for table `ticket`
--
ALTER TABLE `ticket`
  ADD CONSTRAINT `ticket_ibfk_1` FOREIGN KEY (`airline_name`,`flight_num`) REFERENCES `flight` (`airline_name`, `flight_num`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
