## FinSight – Finance Backend Project

## About This Project

This project is a backend system I built to manage financial data like income and expenses with proper access control.

The idea is to simulate a real finance dashboard where different users have different permissions, and data can be processed to generate useful insights.

## Technologies Used

* Python (Flask)
* SQLite (for database)

## What I Implemented

## User Management

* Created users with roles (admin, analyst, viewer)
* Each role has different access permissions

## Financial Records

* Added support for income and expense entries
* Each record includes amount, type, category, date, and notes
* Records can be viewed and filtered
* Records can also be deleted (admin only)

## Access Control

* Implemented role-based access using middleware
* Admin → full access
* Analyst → can view data and dashboard
* Viewer → read-only access

* Access control tested (unauthorized actions return proper errors)

## Authentication Approach

* Authentication is handled using request headers
* The role is passed in each request (example: `role: admin`)
* This simulates authentication and ensures only authorized users can access specific APIs
* This approach keeps the system simple while still enforcing access control

## Dashboard Features

* Total income
* Total expenses
* Net balance
* Category-wise summary
* Recent transactions

## My Approach

Instead of just doing CRUD operations, I focused on:

* Keeping APIs clean and simple
* Adding role-based restrictions
* Writing logic for summary calculations
* Handling cases where data might be empty

## Assumptions

* Authentication is simulated using request headers for simplicity
* All users are pre-authorized and identified by their role
* Data is stored locally using SQLite for easy setup
* The system is designed for backend demonstration and not production use

## API Endpoints

## Users

* POST /users → create user
* GET /users → view users

## Records

* POST /records → add record
* GET /records → view records (supports filtering)
* DELETE /records/{id} → delete a record (admin only)

## Dashboard

* GET /dashboard/summary → overall summary
* GET /dashboard/category → category totals
* GET /dashboard/recent → recent activity

## How to Run

1. Install Flask
   pip install flask

2. Run the server
   python app.py

3. Test APIs using Postman

## Testing

I tested all APIs using Postman and included screenshots of:

* User creation
* Record creation
* Dashboard outputs
* Record deletion

## Notes

* For simplicity, I used request headers to simulate authentication and roles
* SQLite is used for easy setup and local testing

## What I Learned

Through this project, I understood:

* How backend APIs are structured
* How role-based access control works
* How to design endpoints for real-world use cases
* How to handle data aggregation for dashboards

## Future Improvements

* Add JWT-based authentication
* Add pagination and search
* Improve filtering options
* Build frontend dashboard

## Final Thought

This project helped me understand backend development beyond basic CRUD and focus on real-world application logic.
