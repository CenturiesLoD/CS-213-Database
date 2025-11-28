-- Insert Airlines
INSERT INTO airlines(airline_name) VALUES ('Airline A');
INSERT INTO airlines(airline_name) VALUES ('Airline B');



-- Insert Airports
INSERT INTO airports(airport_name, city) VALUES ('PVG', 'Shanghai'), ('JFK', 'New York');

-- Insert 2 Customers and 1 Booking Agent
INSERT INTO customer(customer_email, customer_name, password, address, passport_number, passport_exp_date, passport_country, phone_num, dob) VALUES 
('Person1@mail.com', 'person1', 'pw1', 'address1', '1', '2027-05-15', 'USA', '212-555-0101', '1990-03-15'),
('Person2@mail.com', 'person2',  'pw2', 'address2', '2', '3027-05-15', 'SUA', '212-555-0102', '1990-03-12');


INSERT INTO booking_agent(agent_email, password) VALUES 
('agent1@mail.com', 'pwagent1');

INSERT INTO authorized_by(agent_email, customer_email) VALUES 
('agent1@mail.com', 'Person1@mail.com');

-- Insert 2 airplanes
INSERT INTO airplanes (airplane_id, airline_name, seat_capacity) VALUES 
('FlA', 'Airline A', '10'),('FlB', 'Airline A', '20');
INSERT INTO airplanes (airplane_id, airline_name, seat_capacity) VALUES 
('FlC', 'Airline B', '20'),('FlD', 'Airline B', '50');


-- Inserpt different flights with different progress
INSERT INTO flights (airplane_id, airline_name, arrive_airport, depart_airport, flight_num, departure_time, arrival_time, ticket_price, current_status) VALUES 
('FlA', 'Airline A', 'JFK', 'PVG', 'AA101', '2025-10-15 08:00:00', '2025-10-15 22:30:00', 10, 'upcoming'),
('FlB', 'Airline A', 'PVG', 'JFK', 'AA202', '2025-10-13 14:00:00', '2025-10-13 23:00:00', 20, 'in-progress'),
('FlA', 'Airline A', 'JFK', 'PVG', 'AA303', '2025-10-14 10:00:00', '2025-10-15 02:00:00', 30, 'delayed'),
('FlB', 'Airline A', 'PVG', 'JFK', 'AA404', '2025-10-16 06:00:00', '2025-10-16 18:30:00', 40, 'upcoming');

-- Insert several tickets
INSERT INTO tickets (ticket_id, airline_name, flight_num) VALUES 
(1001, 'Airline A', 'AA101'),
(1002, 'Airline A', 'AA202'),
(1003, 'Airline A', 'AA303'),
(1004, 'Airline A', 'AA404');

-- Then, insert the purchases (child records)
INSERT INTO purchases (ticket_id, customer_email, agent_email, purchase_date) VALUES 
(1001, 'Person1@mail.com', 'agent1@mail.com', '2025-10-01 10:30:00'),  
(1002, 'Person2@mail.com', NULL, '2025-10-02 14:20:00'),              
(1003, 'Person1@mail.com', NULL, '2025-10-03 09:15:00'),              
(1004, 'Person2@mail.com', NULL, '2025-10-04 16:45:00');
