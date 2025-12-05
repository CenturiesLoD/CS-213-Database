-- ============================
-- AIRLINE
-- ============================
INSERT INTO airline (airline_name)
VALUES ('Airline A'), ('Airline B');

-- ============================
-- AIRPORT
-- ============================
INSERT INTO airport (airport_name, airport_city)
VALUES ('PVG', 'Shanghai'),
       ('JFK', 'New York'),
       ('LAX', 'Los Angeles'),
       ('SFO', 'San Francisco');

-- ============================
-- CUSTOMER
-- ============================
INSERT INTO customer (email, name, password, building_number, street, city, state, phone_number, passport_number, passport_expiration, passport_country, date_of_birth)
VALUES
('person1@mail.com', 'Person One', 'pw1', '1', 'Main St', 'NYC', 'NY', '212-555-0101', 'A1234567', '2027-05-15', 'USA', '1990-03-15'),
('person2@mail.com', 'Person Two', 'pw2', '2', 'Second St', 'NYC', 'NY', '212-555-0102', 'B9876543', '2028-08-20', 'USA', '1992-06-10');

-- ============================
-- BOOKING AGENT
-- ============================
INSERT INTO booking_agent (email, password)
VALUES ('agent1@mail.com', 'pwagent1');

-- ============================
-- AIRPLANE
-- ============================
INSERT INTO airplane (airline_name, airplane_id, seat_capacity)
VALUES
('Airline A', 1, 200),
('Airline A', 2, 180),
('Airline B', 3, 220),
('Airline B', 4, 150);

-- ============================
-- FLIGHT
-- ============================
INSERT INTO flight (airline_name, flight_num, departure_airport, departure_time, arrival_airport, arrival_time, price, status, airplane_id)
VALUES
('Airline A', 101, 'PVG', '2025-10-15 08:00:00', 'JFK', '2025-10-15 22:30:00', 1200, 'upcoming', 1),
('Airline A', 202, 'JFK', '2025-10-13 14:00:00', 'PVG', '2025-10-14 06:50:00', 1300, 'in-progress', 2),
('Airline A', 303, 'PVG', '2025-10-14 10:00:00', 'JFK', '2025-10-15 02:00:00', 1400, 'delayed', 1),
('Airline B', 404, 'JFK', '2025-10-16 06:00:00', 'PVG', '2025-10-16 18:30:00', 1100, 'upcoming', 3);

-- ============================
-- TICKET
-- ============================
INSERT INTO ticket (ticket_id, airline_name, flight_num)
VALUES
(1001, 'Airline A', 101),
(1002, 'Airline A', 202),
(1003, 'Airline A', 303),
(1004, 'Airline B', 404);

-- ============================
-- PURCHASES
-- ============================
INSERT INTO purchases (ticket_id, customer_email, booking_agent_email, purchase_date)
VALUES
(1001, 'person1@mail.com', 'agent1@mail.com', '2025-10-01'),
(1002, 'person2@mail.com', NULL, '2025-10-02'),
(1003, 'person1@mail.com', NULL, '2025-10-03'),
(1004, 'person2@mail.com', NULL, '2025-10-04');

INSERT INTO flight (
    airline_name,
    flight_num,
    departure_airport,
    departure_time,
    arrival_airport,
    arrival_time,
    price,
    status,
    airplane_id
) VALUES (
    'DemoAir1',               -- airline_name
    101,                        -- flight_num
    'JFK',                    -- departure_airport
    '2025-1-1 10:00:00',    -- departure_time
    'LAX',                    -- arrival_airport
    '2025-1-1 13:00:00',    -- arrival_time
    350,                      -- price
    'upcoming',               -- status
    1                         -- airplane_id
);