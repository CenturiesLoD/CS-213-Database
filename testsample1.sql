-- Use your database
USE air_reservation;

-- Basic reference data
INSERT INTO airline (airline_name) VALUES ('DemoAir1');

INSERT INTO airplane (airline_name, airplane_id, seat_capacity)
VALUES ('DemoAir1', 1, 180);

INSERT INTO airport (airport_name, airport_city) VALUES
  ('JFK', 'New York'),
  ('LAX', 'Los Angeles');

-- Flights that tickets will reference
INSERT INTO flight (
  airline_name, flight_num,
  departure_airport, departure_time,
  arrival_airport,   arrival_time,
  price, status, airplane_id
) VALUES
  ('DemoAir1', 1001,
   'JFK', '2025-12-20 10:00:00',
   'LAX', '2025-12-20 13:00:00',
   300, 'upcoming', 1),
  ('DemoAir1', 1002,
   'LAX', '2025-09-10 09:00:00',
   'JFK', '2025-09-10 17:00:00',
   250, 'delayed', 1),
  ('DemoAir1', 1003,
   'JFK', '2025-03-05 08:00:00',
   'LAX', '2025-03-05 11:00:00',
   220, 'in-progress', 1);

-- One customer
INSERT INTO customer (
  email, name, password,
  building_number, street, city, state,
  phone_number,
  passport_number, passport_expiration, passport_country,
  date_of_birth
) VALUES (
  'alice@example.com', 'Alice Demo', 'hashedpassword',
  '123', 'Main St', 'New York', 'NY',
  '123-456-7890',
  'P1234567', '2030-01-01', 'USA',
  '1990-05-10'
);

-- Tickets (each ticket_id is unique)
INSERT INTO ticket (ticket_id, airline_name, flight_num) VALUES
  (1, 'DemoAir1', 1001),
  (2, 'DemoAir1', 1001),
  (3, 'DemoAir1', 1002),
  (4, 'DemoAir1', 1002),
  (5, 'DemoAir1', 1003),
  (6, 'DemoAir1', 1003);

-- Purchases:
--   4 within last 6 months (for bar chart),
--   1 within last 12 months but >6 months ago,
--   1 older than 12 months (should be excluded in default view).
INSERT INTO purchases (
  ticket_id, customer_email, booking_agent_email, purchase_date
) VALUES
  -- Last 6 months (assuming “now” ~ Dec 2025)
  (1, 'alice@example.com', NULL, '2025-12-01'), -- December
  (2, 'alice@example.com', NULL, '2025-11-15'), -- November
  (3, 'alice@example.com', NULL, '2025-10-10'), -- October
  (4, 'alice@example.com', NULL, '2025-08-05'), -- August

  -- Within last 12 months but more than 6 months ago
  (5, 'alice@example.com', NULL, '2025-04-20'), -- April

  -- Older than 12 months (should NOT count in total_spending_12m)
  (6, 'alice@example.com', NULL, '2024-10-01'); -- October last year
