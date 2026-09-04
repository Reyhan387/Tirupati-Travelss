from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import and_
import os


# =========================================================
# APPLICATION
# =========================================================

app = Flask(__name__)

app.config["SECRET_KEY"] = "tirupati-yatra-secret-key"

database_path = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    "database",
    "tirupati_yatra.db"
)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///" + database_path
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# =========================================================
# USER
# =========================================================

class User(db.Model):

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    mobile = db.Column(
        db.String(15),
        nullable=False
    )

    password = db.Column(
        db.String(100),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        nullable=False,
        default="customer"
    )


# =========================================================
# BUS
# =========================================================

class Bus(db.Model):

    __tablename__ = "buses"

    bus_id = db.Column(
        db.Integer,
        primary_key=True
    )

    bus_number = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    bus_name = db.Column(
        db.String(100),
        nullable=False
    )

    total_seats = db.Column(
        db.Integer,
        nullable=False
    )


# =========================================================
# ROUTE
# =========================================================

class Route(db.Model):

    __tablename__ = "routes"

    route_id = db.Column(
        db.Integer,
        primary_key=True
    )

    source = db.Column(
        db.String(100),
        nullable=False
    )

    destination = db.Column(
        db.String(100),
        nullable=False
    )


# =========================================================
# TRIP
# =========================================================

class Trip(db.Model):

    __tablename__ = "trips"

    trip_id = db.Column(
        db.Integer,
        primary_key=True
    )

    bus_id = db.Column(
        db.Integer,
        db.ForeignKey("buses.bus_id"),
        nullable=False
    )

    route_id = db.Column(
        db.Integer,
        db.ForeignKey("routes.route_id"),
        nullable=False
    )

    travel_date = db.Column(
        db.Date,
        nullable=False
    )

    departure_time = db.Column(
        db.String(10),
        nullable=False
    )

    price = db.Column(
        db.Float,
        nullable=False
    )

    available_seats = db.Column(
        db.Integer,
        nullable=False
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Active"
    )

    bus = db.relationship(
        "Bus",
        backref="trips"
    )

    route = db.relationship(
        "Route",
        backref="trips"
    )


# =========================================================
# SEAT
# =========================================================

class Seat(db.Model):

    __tablename__ = "seats"

    seat_id = db.Column(
        db.Integer,
        primary_key=True
    )

    bus_id = db.Column(
        db.Integer,
        db.ForeignKey("buses.bus_id"),
        nullable=False
    )

    seat_number = db.Column(
        db.String(10),
        nullable=False
    )

    seat_type = db.Column(
        db.String(20),
        nullable=False,
        default="Aisle"
    )


# =========================================================
# BOOKING
# =========================================================

class Booking(db.Model):

    __tablename__ = "bookings"

    booking_id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    trip_id = db.Column(
        db.Integer,
        db.ForeignKey("trips.trip_id"),
        nullable=False
    )

    booking_date = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    total_amount = db.Column(
        db.Float,
        nullable=False
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Pending"
    )

    user = db.relationship(
        "User",
        backref="bookings"
    )

    trip = db.relationship(
        "Trip",
        backref="bookings"
    )


# =========================================================
# BOOKING SEAT
# =========================================================

class BookingSeat(db.Model):

    __tablename__ = "booking_seats"

    booking_seat_id = db.Column(
        db.Integer,
        primary_key=True
    )

    booking_id = db.Column(
        db.Integer,
        db.ForeignKey("bookings.booking_id"),
        nullable=False
    )

    seat_id = db.Column(
        db.Integer,
        db.ForeignKey("seats.seat_id"),
        nullable=False
    )

    booking = db.relationship(
        "Booking",
        backref="booking_seats"
    )

    seat = db.relationship(
        "Seat",
        backref="booking_seats"
    )


# =========================================================
# PAYMENT
# =========================================================

class Payment(db.Model):

    __tablename__ = "payments"

    payment_id = db.Column(
        db.Integer,
        primary_key=True
    )

    booking_id = db.Column(
        db.Integer,
        db.ForeignKey("bookings.booking_id"),
        nullable=False
    )

    amount = db.Column(
        db.Float,
        nullable=False
    )

    payment_method = db.Column(
        db.String(30),
        nullable=False
    )

    payment_status = db.Column(
        db.String(20),
        nullable=False,
        default="Pending"
    )

    payment_date = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    booking = db.relationship(
        "Booking",
        backref="payments"
    )


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template("index.html")


# =========================================================
# SEARCH BUS
# =========================================================

@app.route("/search", methods=["POST"])
def search():

    source = request.form.get(
        "source",
        ""
    ).strip()

    destination = request.form.get(
        "destination",
        ""
    ).strip()

    travel_date_text = request.form.get(
        "travel_date",
        ""
    ).strip()

    if not source or not destination or not travel_date_text:

        return render_template(
            "search_results.html",
            trips=[],
            error="Please enter From, To and Travel Date."
        )

    try:

        travel_date = datetime.strptime(
            travel_date_text,
            "%Y-%m-%d"
        ).date()

    except ValueError:

        return render_template(
            "search_results.html",
            trips=[],
            error="Invalid travel date."
        )

    trips = (
        Trip.query
        .join(Route)
        .filter(
            Route.source == source,
            Route.destination == destination,
            Trip.travel_date == travel_date,
            Trip.status == "Active",
            Trip.available_seats > 0
        )
        .all()
    )

    return render_template(
        "search_results.html",
        trips=trips,
        error=None
    )


# =========================================================
# SELECT BUS / SEATS
# =========================================================

@app.route("/select-bus/<int:trip_id>")
def select_bus(trip_id):

    trip = Trip.query.get_or_404(trip_id)

    seats = (
        Seat.query
        .filter_by(bus_id=trip.bus_id)
        .order_by(Seat.seat_id)
        .all()
    )

    # Find seats already booked for this trip
    booked_seat_ids = [
        item.seat_id
        for item in (
            BookingSeat.query
            .join(Booking)
            .filter(
                Booking.trip_id == trip_id,
                Booking.status.in_(
                    ["Pending", "Confirmed"]
                )
            )
            .all()
        )
    ]

    return render_template(
        "seats.html",
        trip=trip,
        seats=seats,
        booked_seat_ids=booked_seat_ids
    )


# =========================================================
# PASSENGER DETAILS
# =========================================================

@app.route(
    "/passenger-details/<int:trip_id>",
    methods=["POST"]
)
def passenger_details(trip_id):

    trip = Trip.query.get_or_404(trip_id)

    seat_id = request.form.get("seat_id")

    if not seat_id:

        return redirect(
            url_for(
                "select_bus",
                trip_id=trip_id
            )
        )

    try:
        seat_id = int(seat_id)

    except ValueError:

        return redirect(
            url_for(
                "select_bus",
                trip_id=trip_id
            )
        )

    seat = Seat.query.get_or_404(seat_id)

    if seat.bus_id != trip.bus_id:

        return "Invalid seat for this bus."

    existing_booking = (
        BookingSeat.query
        .join(Booking)
        .filter(
            Booking.trip_id == trip_id,
            BookingSeat.seat_id == seat_id,
            Booking.status.in_(
                ["Pending", "Confirmed"]
            )
        )
        .first()
    )

    if existing_booking:

        return "Sorry, this seat is already booked."

    return render_template(
        "passenger_details.html",
        trip=trip,
        seat=seat
    )


# =========================================================
# REVIEW BOOKING
# =========================================================

@app.route(
    "/review-booking/<int:trip_id>",
    methods=["POST"]
)
def review_booking(trip_id):

    trip = Trip.query.get_or_404(trip_id)

    seat_id = request.form.get("seat_id")

    passenger_name = request.form.get(
        "passenger_name",
        ""
    ).strip()

    mobile = request.form.get(
        "mobile",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip()

    if not passenger_name or not mobile or not email:

        return "Please enter all passenger details."

    try:

        seat_id = int(seat_id)

    except (ValueError, TypeError):

        return "Invalid seat."

    seat = Seat.query.get_or_404(seat_id)

    if seat.bus_id != trip.bus_id:

        return "Invalid seat for this bus."

    existing_booking = (
        BookingSeat.query
        .join(Booking)
        .filter(
            Booking.trip_id == trip_id,
            BookingSeat.seat_id == seat_id,
            Booking.status.in_(
                ["Pending", "Confirmed"]
            )
        )
        .first()
    )

    if existing_booking:

        return "Sorry, this seat has just been booked."

    return render_template(
        "review_booking.html",
        trip=trip,
        seat=seat,
        passenger_name=passenger_name,
        mobile=mobile,
        email=email
    )


# =========================================================
# CREATE BOOKING
# =========================================================

@app.route(
    "/create-booking/<int:trip_id>",
    methods=["POST"]
)
def create_booking(trip_id):

    trip = Trip.query.get_or_404(trip_id)

    seat_id = request.form.get("seat_id")

    passenger_name = request.form.get(
        "passenger_name",
        ""
    ).strip()

    mobile = request.form.get(
        "mobile",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip()

    if not seat_id or not passenger_name or not mobile or not email:

        return "All passenger details are required."

    try:

        seat_id = int(seat_id)

    except ValueError:

        return "Invalid seat."

    seat = Seat.query.get_or_404(seat_id)

    if seat.bus_id != trip.bus_id:

        return "Invalid seat for this bus."

    # Check seat again before creating booking
    existing_booking = (
        BookingSeat.query
        .join(Booking)
        .filter(
            Booking.trip_id == trip_id,
            BookingSeat.seat_id == seat_id,
            Booking.status.in_(
                ["Pending", "Confirmed"]
            )
        )
        .first()
    )

    if existing_booking:

        return "Sorry, this seat is already booked."

    if trip.available_seats <= 0:

        return "Sorry, no seats are available."

    # Find existing customer
    user = User.query.filter_by(
        email=email
    ).first()

    if not user:

        user = User(
            name=passenger_name,
            email=email,
            mobile=mobile,
            password="",
            role="customer"
        )

        db.session.add(user)

        db.session.flush()

    else:

        user.name = passenger_name
        user.mobile = mobile

    # Create pending booking
    booking = Booking(
        user_id=user.user_id,
        trip_id=trip.trip_id,
        total_amount=trip.price,
        status="Pending"
    )

    db.session.add(booking)

    db.session.flush()

    booking_seat = BookingSeat(
        booking_id=booking.booking_id,
        seat_id=seat.seat_id
    )

    db.session.add(booking_seat)

    trip.available_seats -= 1

    db.session.commit()

    return redirect(
        url_for(
            "payment",
            booking_id=booking.booking_id
        )
    )


# =========================================================
# PAYMENT PAGE
# =========================================================

@app.route("/payment/<int:booking_id>")
def payment(booking_id):

    booking = Booking.query.get_or_404(
        booking_id
    )

    trip = booking.trip

    if booking.status == "Cancelled":

        return "This booking has been cancelled."

    return render_template(
        "payment.html",
        booking=booking,
        trip=trip
    )


# =========================================================
# PROCESS PAYMENT
# =========================================================

@app.route(
    "/process-payment/<int:booking_id>",
    methods=["POST"]
)
def process_payment(booking_id):

    booking = Booking.query.get_or_404(
        booking_id
    )

    if booking.status == "Cancelled":

        return "This booking has already been cancelled."

    payment_method = request.form.get(
        "payment_method",
        ""
    ).strip()

    if payment_method not in [
        "UPI",
        "Debit / Credit Card",
        "Cash"
    ]:

        return "Invalid payment method."

    # Prevent duplicate successful payment
    existing_payment = Payment.query.filter_by(
        booking_id=booking.booking_id,
        payment_status="Success"
    ).first()

    if existing_payment:

        return redirect(
            url_for(
                "payment_success",
                booking_id=booking.booking_id
            )
        )

    payment = Payment(
        booking_id=booking.booking_id,
        amount=booking.total_amount,
        payment_method=payment_method,
        payment_status="Success"
    )

    db.session.add(payment)

    # Payment successful → confirm booking
    booking.status = "Confirmed"

    db.session.commit()

    return redirect(
        url_for(
            "payment_success",
            booking_id=booking.booking_id
        )
    )


# =========================================================
# PAYMENT SUCCESS
# =========================================================

@app.route(
    "/payment-success/<int:booking_id>"
)
def payment_success(booking_id):

    booking = Booking.query.get_or_404(
        booking_id
    )

    payment = (
        Payment.query
        .filter_by(
            booking_id=booking.booking_id,
            payment_status="Success"
        )
        .order_by(
            Payment.payment_id.desc()
        )
        .first()
    )

    if not payment:

        return "Payment not found."

    return render_template(
        "payment_success.html",
        booking=booking,
        payment=payment
    )


# =========================================================
# CANCEL BOOKING
# =========================================================

@app.route(
    "/cancel-booking/<int:booking_id>",
    methods=["POST"]
)
def cancel_booking(booking_id):

    booking = Booking.query.get_or_404(
        booking_id
    )

    if booking.status == "Cancelled":

        return redirect(
            url_for(
                "booking_cancelled",
                booking_id=booking.booking_id
            )
        )

    # Only confirmed/pending bookings can be cancelled
    if booking.status not in [
        "Pending",
        "Confirmed"
    ]:

        return "Booking cannot be cancelled."

    # Cancel booking
    booking.status = "Cancelled"

    # Return seat to availability
    booking.trip.available_seats += 1

    # Cancel related pending/success payment status
    for payment in booking.payments:

        if payment.payment_status == "Success":

            payment.payment_status = "Refund Pending"

    db.session.commit()

    return redirect(
        url_for(
            "booking_cancelled",
            booking_id=booking.booking_id
        )
    )


# =========================================================
# BOOKING CANCELLED
# =========================================================

@app.route(
    "/booking-cancelled/<int:booking_id>"
)
def booking_cancelled(booking_id):

    booking = Booking.query.get_or_404(
        booking_id
    )

    trip = booking.trip

    return render_template(
        "booking_cancelled.html",
        booking=booking,
        trip=trip
    )


# =========================================================
# ERROR HANDLER
# =========================================================

@app.errorhandler(404)
def page_not_found(error):

    return """
    <h1>Page Not Found</h1>
    <p>The requested page does not exist.</p>
    <a href="/">Go Home</a>
    """, 404


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )