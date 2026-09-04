from app import (
    app,
    db,
    User,
    Bus,
    Route,
    Trip,
    Seat
)

from datetime import date


# ==========================================
# INSERT SAMPLE DATA
# ==========================================

with app.app_context():

    print("Starting database setup...")


    # --------------------------------------
    # 1. CREATE USER
    # --------------------------------------

    user = User(
        name="Reyhan",
        email="reyhan@example.com",
        mobile="9876543210",
        password="123456",
        role="customer"
    )

    db.session.add(user)


    # --------------------------------------
    # 2. CREATE BUSES
    # --------------------------------------

    bus1 = Bus(
        bus_number="MH15AB1234",
        bus_name="Tirupati Express",
        total_seats=40
    )

    bus2 = Bus(
        bus_number="MH15CD5678",
        bus_name="Yatra Travels",
        total_seats=40
    )

    db.session.add(bus1)
    db.session.add(bus2)

    db.session.commit()


    # --------------------------------------
    # 3. CREATE ROUTES
    # --------------------------------------

    route1 = Route(
        source="Kopargaon",
        destination="Tirupati"
    )

    route2 = Route(
        source="Nashik",
        destination="Tirupati"
    )

    db.session.add(route1)
    db.session.add(route2)

    db.session.commit()


    # --------------------------------------
    # 4. CREATE TRIPS
    # --------------------------------------

    trip1 = Trip(
        bus_id=bus1.bus_id,
        route_id=route1.route_id,
        travel_date=date(2026, 8, 25),
        departure_time="07:00 PM",
        price=1200,
        available_seats=40,
        status="Active"
    )

    trip2 = Trip(
        bus_id=bus2.bus_id,
        route_id=route2.route_id,
        travel_date=date(2026, 8, 26),
        departure_time="08:00 PM",
        price=1400,
        available_seats=40,
        status="Active"
    )

    db.session.add(trip1)
    db.session.add(trip2)


    # --------------------------------------
    # 5. CREATE SEATS FOR BUS 1
    # --------------------------------------

    for row in range(1, 21):

        seat_a = Seat(
            bus_id=bus1.bus_id,
            seat_number=f"{row}A",
            seat_type="Window"
        )

        seat_b = Seat(
            bus_id=bus1.bus_id,
            seat_number=f"{row}B",
            seat_type="Aisle"
        )

        db.session.add(seat_a)
        db.session.add(seat_b)


    # --------------------------------------
    # 6. CREATE SEATS FOR BUS 2
    # --------------------------------------

    for row in range(1, 21):

        seat_a = Seat(
            bus_id=bus2.bus_id,
            seat_number=f"{row}A",
            seat_type="Window"
        )

        seat_b = Seat(
            bus_id=bus2.bus_id,
            seat_number=f"{row}B",
            seat_type="Aisle"
        )

        db.session.add(seat_a)
        db.session.add(seat_b)


    # --------------------------------------
    # SAVE EVERYTHING
    # --------------------------------------

    db.session.commit()

    print("Sample data inserted successfully!")
