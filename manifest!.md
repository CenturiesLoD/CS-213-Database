├── agent (Everything pertaining to booking agents)
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-312.pyc
│   │   └── routes.cpython-312.pyc
│   └── routes.py (Used for routing in Flask related to booking agent)
├── air_reservation_dec8.sql (Database setup)
├── antiauto_challenge_city (Left over. Did city as anti-auto challenge)
├── app.py (Main file, run from here)
├── auth (Everything pertaining to authentication such as login and registration)
│   ├── forms!.py
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-312.pyc
│   │   └── routes.cpython-312.pyc
│   └── routes.py (Used for routing in Flask related to authentication)
├── customer
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-312.pyc
│   │   └── routes.cpython-312.pyc
│   └── routes.py (Used for routing in Flask related to customer)
├── db.py (Used for connection to the local DB)
├── feature_query_map!.md
├── LICENSE
├── manifest!.md
├── passwordgen.py (Used for testing)
├── public (Everything pertaining to user without any login ins)
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-312.pyc
│   │   └── routes.cpython-312.pyc
│   └── routes.py (Used for routing in Flask related to unlogged in user)
├── __pycache__
│   └── db.cpython-312.pyc
├── README.md
├── requirements.txt
├── sampledata.sql (Old test files)
├── staff (Everything pertaining to staff)
│   ├── admin_routes.py (Used for routing in Flask related to admin)
│   ├── __init__.py
│   ├── operator_routes.py (Used for routing in Flask related to operator)
│   ├── __pycache__
│   │   ├── admin_routes.cpython-312.pyc
│   │   ├── __init__.cpython-312.pyc
│   │   ├── operator_routes.cpython-312.pyc
│   │   └── routes.cpython-312.pyc
│   └── routes.py (Used for routing in Flask related to general staff)
├── team_contribution!.md
├── templates (HTML files used for Flask. The many for these individual files are self-explanatory as they either refer to a stated feature desired inside of the Project Narrative)
│   ├── agent (Pertains to agent)
│   │   ├── analytics_commission.html
│   │   ├── analytics_top_customers.html
│   │   ├── dashboard.html
│   │   ├── debug_airlines.html (Debug file to that shows the agent’s authorized airlines)
│   │   ├── flights.html
│   │   └── search.html
│   ├── auth (Pertains to authentication)
│   │   ├── choose_user_type.html
│   │   ├── register_agent.html
│   │   ├── register_customer.html
│   │   └── register_staff.html
│   ├── base.html (Base HTML file. Other HTML files extend this. Can be thought of as home).
│   ├── customer (Pertains to customer)
│   │   ├── dashboard.html
│   │   ├── flights.html
│   │   ├── purchase.html
│   │   ├── search.html
│   │   ├── search_results.html
│   │   ├── spending_custom.html
│   │   └── spending_default.html
│   ├── index.html (Used to present login/registration, as well as dashboards)
│   ├── login.html (Specific login page. Used for all user types)
│   ├── public_search_in_progress.html (All usertypes search through this since it makes no sense for different users to be able to search different when it comes to in progress flights.)
│   ├── public_search_upcoming.html (All search requests pass through here first, before being redirected to the unique searches of different user types)
│   ├── register.html (Page for registration. Same page for all usertypes)
│   ├── staff
│       ├── admin_add_airplane.html
│       ├── admin_add_airport.html
│       ├── admin_authorize_agent.html
│       ├── admin_create_flight.html
│       ├── analytics_agents.html
│       ├── analytics_customers.html
│       ├── analytics_destinations.html
│       ├── customer_history.html
│       ├── dashboard.html
│       ├── flight_search.html
│       ├── flights_next30.html
│       ├── operator_update_status.html
│       └── passengeer_list.html
├── testsample1.sql 

