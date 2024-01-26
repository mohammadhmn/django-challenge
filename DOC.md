# Ticketing Project Documentation

## Overview

The Ticketing project aims to implement an online selling platform for the Volleyball Federation's next season. The platform allows users to sign up and log in, add new stadiums, define matches, specify the place of seats for each match, and purchase seats for a match.

## Django Version

This project is developed using Django version 5.0.1.

## Features

### 1. User Sign-up and Sign-in

- Users can sign up with their details.
- Registered users can sign in to the platform.

### 2. Adding a New Stadium

- Admins can add new stadiums to the platform.

### 3. Defining Matches

- Admins can define matches, specifying details such as teams, date, and time.

### 4. Defining the Place of Seats for Each Match

- Admins can set up the seating arrangement for each match, defining the layout and available seats.

### 5. Buying Seats of a Match

- Users can purchase tickets for a specific match.
- The system updates seat availability in real-time.

## Third-Party Packages:

This project utilizes the Django Rest Framework for building the API.

## How to Run the Project:

1. Navigate to the project directory: cd into project directory
2. Install dependencies: pip install -r requirements.txt
3. Apply migrations: python manage.py migrate
4. Run the development server: python manage.py runserver

## Handling Concurrent Seat Reservations:

This project employs optimistic updating to handle concurrent seat reservations efficiently.

Optimistic updating is a strategy used to handle concurrent updates in web applications. In the `ReserveSeatView`:

- Users request to reserve a seat for a match.
- The server checks if the seat and match exist.
- It attempts to create a reservation.
- Before saving, it updates the seat's timestamp.
- If another update occurred since the user's request, a conflict is detected.
- In case of conflict, the reservation is rolled back, and a conflict response is sent.
- If no conflict, the reservation is created, and a success response is sent.

This prevents conflicts when multiple users try to reserve the same seat simultaneously. The client needs to handle conflict responses by refreshing data and resubmitting changes if necessary.
